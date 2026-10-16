export const CHAT_UI_REOPEN = "___keplerllm-chat-widget-open___";
export function parseStylesSrc(scriptSrc = null) {
  try {
    const _url = new URL(scriptSrc);
    _url.pathname = _url.pathname
      .replace("keplerllm-chat-widget.js", "keplerllm-chat-widget.min.css")
      .replace(
        "keplerllm-chat-widget.min.js",
        "keplerllm-chat-widget.min.css"
      );
    return _url.toString();
  } catch {
    return "";
  }
}
