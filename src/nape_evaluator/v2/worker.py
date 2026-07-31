"""Fresh isolated worker for attestify-python-test-development-v1.

The supervisor is the only public protocol writer.  This process accepts one
private control object and emits one private result object.
"""

from __future__ import annotations

import ast
import builtins
import contextlib
import io
import json
import resource
import sys
import types


CPYTHON_VERSION = (3, 11, 6)
MAX_TEST_FRAMES = 256
CPU_SECONDS = 30
ADDRESS_SPACE_BYTES = 1_073_741_824

_BUILTIN_NAMES = {
    "Exception",
    "TypeError",
    "UnicodeDecodeError",
    "ValueError",
    "bool",
    "bytes",
    "dict",
    "enumerate",
    "float",
    "int",
    "isinstance",
    "len",
    "list",
    "max",
    "min",
    "range",
    "set",
    "str",
    "sum",
    "tuple",
    "zip",
}

_DENIED_NODES = (
    ast.AsyncFor,
    ast.AsyncFunctionDef,
    ast.AsyncWith,
    ast.Await,
    ast.ClassDef,
    ast.Delete,
    ast.Global,
    ast.Lambda,
    ast.Match,
    ast.NamedExpr,
    ast.Nonlocal,
    ast.Starred,
    ast.TryStar,
    ast.With,
    ast.Yield,
    ast.YieldFrom,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)


class _WorkLimit(BaseException):
    pass


class _DepthLimit(BaseException):
    pass


class _SandboxViolation(BaseException):
    pass


class _AdmissionFailure(Exception):
    pass


class _ProfileJson:
    loads = staticmethod(json.loads)
    JSONDecodeError = json.JSONDecodeError


def _fail(message: str) -> None:
    raise _AdmissionFailure(message)


class _Admission(ast.NodeVisitor):
    def __init__(self):
        self.functions = set()
        self.function_depth = 0

    def visit_Module(self, node):
        for child in node.body:
            if isinstance(child, ast.Import):
                if (
                    len(child.names) != 1
                    or child.names[0].name != "json"
                    or child.names[0].asname is not None
                ):
                    _fail("import")
            elif isinstance(child, ast.Assign):
                if (
                    len(child.targets) != 1
                    or not isinstance(child.targets[0], ast.Name)
                    or not isinstance(child.value, ast.Constant)
                    or not isinstance(child.value.value, (str, bytes, int, float, bool, type(None)))
                ):
                    _fail("top-level assignment")
            elif isinstance(child, ast.FunctionDef):
                self.functions.add(child.name)
            else:
                _fail("top-level form")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        if self.function_depth:
            _fail("nested function")
        if node.decorator_list or node.returns is not None or node.type_comment is not None:
            _fail("function decoration")
        args = node.args
        if (
            args.posonlyargs
            or args.kwonlyargs
            or args.vararg is not None
            or args.kwarg is not None
            or args.defaults
            or args.kw_defaults
            or any(argument.annotation is not None for argument in args.args)
        ):
            _fail("function signature")
        self.function_depth += 1
        self.generic_visit(node)
        self.function_depth -= 1

    def visit_ExceptHandler(self, node):
        permitted_names = {
            "Exception",
            "TypeError",
            "UnicodeDecodeError",
            "ValueError",
        }

        def permitted(candidate):
            if isinstance(candidate, ast.Name):
                return candidate.id in permitted_names
            if isinstance(candidate, ast.Attribute):
                return (
                    isinstance(candidate.value, ast.Name)
                    and candidate.value.id == "json"
                    and candidate.attr == "JSONDecodeError"
                )
            if isinstance(candidate, ast.Tuple):
                return bool(candidate.elts) and all(
                    permitted(item) for item in candidate.elts
                )
            return False

        if node.type is None or not permitted(node.type):
            _fail("exception handler")
        self.generic_visit(node)

    def visit_Import(self, node):
        if self.function_depth:
            _fail("nested import")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        _fail("import-from")

    def visit_Name(self, node):
        if "__" in node.id:
            _fail("dunder identifier")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if "__" in node.attr or node.attr not in ("loads", "JSONDecodeError", "decode", "get"):
            _fail("attribute")
        if node.attr in ("loads", "JSONDecodeError"):
            if not isinstance(node.value, ast.Name) or node.value.id != "json":
                _fail("json receiver")
        self.generic_visit(node)

    def visit_Call(self, node):
        target = node.func
        if isinstance(target, ast.Name):
            if target.id not in _BUILTIN_NAMES and target.id not in self.functions:
                _fail("call target")
        elif isinstance(target, ast.Attribute):
            if target.attr == "decode":
                if (
                    not isinstance(target.value, ast.Name)
                    or target.value.id != "evidence"
                    or len(node.args) != 1
                    or not isinstance(node.args[0], ast.Constant)
                    or node.args[0].value != "utf-8"
                    or len(node.keywords) != 1
                    or node.keywords[0].arg != "errors"
                    or not isinstance(node.keywords[0].value, ast.Constant)
                    or node.keywords[0].value.value != "strict"
                ):
                    _fail("decode call")
            elif target.attr == "get":
                if not (1 <= len(node.args) <= 2) or node.keywords:
                    _fail("dict get call")
                if isinstance(target.value, ast.Name) and target.value.id in (
                    "metadata",
                    "evaluations",
                ):
                    _fail("evaluator-owned dict receiver")
            elif target.attr == "loads":
                if not isinstance(target.value, ast.Name) or target.value.id != "json":
                    _fail("json loads receiver")
                if len(node.args) != 1:
                    _fail("json loads arguments")
                if any(
                    keyword.arg not in ("object_pairs_hook", "parse_constant")
                    or not isinstance(keyword.value, ast.Name)
                    or keyword.value.id not in self.functions
                    for keyword in node.keywords
                ):
                    _fail("json loads keyword")
            else:
                _fail("attribute call")
        else:
            _fail("dynamic call")
        self.generic_visit(node)

    def generic_visit(self, node):
        if isinstance(node, _DENIED_NODES):
            _fail("syntax")
        super().generic_visit(node)


def _validate_abi(tree: ast.Module) -> None:
    definitions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "evaluate"
    ]
    if len(definitions) != 1:
        _fail("evaluate entry point")
    args = definitions[0].args
    if [item.arg for item in args.args] != ["evidence", "evaluations", "metadata"]:
        _fail("evaluate ABI")


def _owned_codes(code):
    result = {code}
    for constant in code.co_consts:
        if isinstance(constant, types.CodeType):
            result.update(_owned_codes(constant))
    return result


def _install_resources() -> None:
    if sys.implementation.name != "cpython" or sys.version_info[:3] != CPYTHON_VERSION:
        raise _AdmissionFailure("runtime closure")
    # The soft limit is the normative backstop. The one-second hard margin
    # guarantees termination even if host signal disposition is abnormal.
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS + 1))
    resource.setrlimit(
        resource.RLIMIT_AS, (ADDRESS_SPACE_BYTES, ADDRESS_SPACE_BYTES)
    )


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "json" and not fromlist and level == 0:
        return _ProfileJson
    raise _SandboxViolation()


def _restricted_builtins():
    result = {name: getattr(builtins, name) for name in _BUILTIN_NAMES}
    result["__import__"] = _safe_import
    return result


def _execute(control):
    _install_resources()
    source = bytes.fromhex(control["source_hex"])
    evidence = bytes.fromhex(control["evidence_hex"])
    maximum = control["maximum_execution_work_units"]
    try:
        source_text = source.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise _AdmissionFailure("source encoding")
    if source.startswith(b"\xef\xbb\xbf"):
        raise _AdmissionFailure("source BOM")
    tree = ast.parse(source_text, filename="<admitted-test>", mode="exec")
    admission = _Admission()
    admission.visit(tree)
    _validate_abi(tree)
    sys.stderr.buffer.write(b"ATTESTIFY_WORKER_READY\n")
    sys.stderr.buffer.flush()
    code = compile(tree, "<admitted-test>", "exec", dont_inherit=True, optimize=0)
    realm = {
        "__builtins__": _restricted_builtins(),
        "__name__": "attestify_admitted_test",
    }
    protected_stdout = io.StringIO()
    protected_stderr = io.StringIO()
    try:
        with contextlib.redirect_stdout(protected_stdout), contextlib.redirect_stderr(
            protected_stderr
        ):
            exec(code, realm, realm)
    except _SandboxViolation:
        return {
            "kind": "contained",
            "code": "test_sandbox_capability_violation",
            "phase": "module-initialization",
            "call_count": 0,
        }
    except BaseException:
        return {
            "kind": "contained",
            "code": "test_exception",
            "phase": "module-initialization",
            "call_count": 0,
        }
    evaluate = realm.get("evaluate")
    if not isinstance(evaluate, types.FunctionType):
        raise _AdmissionFailure("evaluate activation")
    sys.stderr.buffer.write(b"ATTESTIFY_EVALUATE_READY\n")
    sys.stderr.buffer.flush()

    work = (len(source) + 15) // 16 + (len(evidence) + 15) // 16 + 256
    if work > maximum:
        return {
            "kind": "contained",
            "code": "test_execution_work_limit_exceeded",
            "phase": "evaluate-call",
            "call_count": 1,
        }
    owned = _owned_codes(code)
    active_depth = 0

    def trace(frame, event, arg):
        nonlocal work, active_depth
        if frame.f_code not in owned:
            return None
        if event == "call":
            active_depth += 1
            if active_depth > MAX_TEST_FRAMES:
                raise _DepthLimit()
            frame.f_trace_opcodes = True
            return trace
        if event == "return":
            active_depth -= 1
            return trace
        if event == "opcode":
            if work + 1 > maximum:
                raise _WorkLimit()
            work += 1
        return trace

    try:
        sys.settrace(trace)
        with contextlib.redirect_stdout(protected_stdout), contextlib.redirect_stderr(
            protected_stderr
        ):
            result = evaluate(
                evidence,
                [],
                {
                    "evidence_media_type": control["metadata"]["evidence_media_type"],
                    "evidence_representation": control["metadata"][
                        "evidence_representation"
                    ],
                    "evaluator_contract_version": control["metadata"][
                        "evaluator_contract_version"
                    ],
                },
            )
    except _WorkLimit:
        return {
            "kind": "contained",
            "code": "test_execution_work_limit_exceeded",
            "phase": "evaluate-call",
            "call_count": 1,
        }
    except _DepthLimit:
        return {
            "kind": "contained",
            "code": "test_call_depth_exceeded",
            "phase": "evaluate-call",
            "call_count": 1,
        }
    except _SandboxViolation:
        return {
            "kind": "contained",
            "code": "test_sandbox_capability_violation",
            "phase": "evaluate-call",
            "call_count": 1,
        }
    except MemoryError:
        return {
            "kind": "contained",
            "code": "test_memory_backstop_exceeded",
            "phase": "evaluate-call",
            "call_count": 1,
        }
    except BaseException:
        return {
            "kind": "contained",
            "code": "test_exception",
            "phase": "evaluate-call",
            "call_count": 1,
        }
    finally:
        sys.settrace(None)
    return {"kind": "returned", "result": result}


def main() -> int:
    try:
        control = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        result = _execute(control)
    except _AdmissionFailure:
        result = {"kind": "blocked", "code": "runner_activation_failed"}
    except BaseException:
        result = {"kind": "blocked", "code": "runner_activation_failed"}
    try:
        encoded = json.dumps(
            result,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except BaseException:
        encoded = b'{"kind":"returned","result":null}'
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
