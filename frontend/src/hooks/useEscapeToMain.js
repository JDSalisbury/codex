import { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

/**
 * Global Escape → navigate to main menu ("/")
 *
 * Options:
 * - enabled: turn on/off
 * - mainPath: default "/"
 * - ignoreWhenTyping: don't fire while typing in inputs
 * - preventDefault: default true
 */
export function useEscapeToMain({
  enabled = true,
  mainPath = "/menu",
  ignoreWhenTyping = true,
  preventDefault = true,
} = {}) {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (!enabled) return;

    const onKeyDown = (e) => {
      if (e.key !== "Escape") return;

      if (ignoreWhenTyping) {
        const el = document.activeElement;
        const isTypingTarget =
          el &&
          (el.tagName === "INPUT" ||
            el.tagName === "TEXTAREA" ||
            el.isContentEditable);
        if (isTypingTarget) return;
      }

      if (preventDefault) e.preventDefault();

      // Avoid pointless navigation if already on main
      if (location.pathname === mainPath) return;

      navigate(mainPath);
    };

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    enabled,
    navigate,
    location.pathname,
    mainPath,
    ignoreWhenTyping,
    preventDefault,
  ]);
}
