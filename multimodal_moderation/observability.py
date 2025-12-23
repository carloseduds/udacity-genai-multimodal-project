from opentelemetry import trace


def get_trace_ids() -> tuple[str | None, str | None]:
    span = trace.get_current_span()
    ctx = span.get_span_context() if span else None
    if not ctx or not ctx.is_valid:
        return None, None

    trace_id = format(ctx.trace_id, "032x")
    span_id = format(ctx.span_id, "016x")
    return trace_id, span_id
