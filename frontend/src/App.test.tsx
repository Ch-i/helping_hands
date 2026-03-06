import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";

import App from "./App";

// Mock fetch globally so the component's network calls don't fail.
beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({}),
      text: async () => "",
    })
  );

  // Mock Notification API (not available in jsdom)
  vi.stubGlobal("Notification", { permission: "denied" });

  // Mock serviceWorker.register so the useEffect doesn't crash
  Object.defineProperty(navigator, "serviceWorker", {
    value: {
      register: vi.fn().mockResolvedValue({ active: null }),
      ready: Promise.resolve({ active: null }),
    },
    configurable: true,
    writable: true,
  });
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("App component", () => {
  it("renders without crashing", () => {
    render(<App />);
    // The submit button is always visible
    expect(screen.getByText("Run")).toBeInTheDocument();
  });

  it("renders the repo path input with default value", () => {
    render(<App />);
    const repoInput = screen.getByPlaceholderText("owner/repo");
    expect(repoInput).toBeInTheDocument();
    expect(repoInput).toHaveValue("suryarastogi/helping_hands");
  });

  it("renders the prompt input with default value", () => {
    render(<App />);
    const promptInput = screen.getByPlaceholderText("Prompt");
    expect(promptInput).toBeInTheDocument();
    expect(promptInput).toHaveValue(
      "Update README.md with results of your smoke test. Keep changes minimal and safe."
    );
  });

  it("renders the empty task list message", () => {
    render(<App />);
    expect(screen.getByText("No tasks submitted yet.")).toBeInTheDocument();
  });

  it("renders the service health bar", () => {
    render(<App />);
    expect(screen.getByLabelText("Service health")).toBeInTheDocument();
  });

  it("renders the dashboard view toggle buttons", () => {
    render(<App />);
    expect(screen.getByText("Classic view")).toBeInTheDocument();
    expect(screen.getByText("Hand world")).toBeInTheDocument();
  });

  it("renders the new submission and scheduled tasks buttons", () => {
    render(<App />);
    expect(screen.getByText("New submission")).toBeInTheDocument();
    expect(screen.getByText("Scheduled tasks")).toBeInTheDocument();
  });

  it("renders the submitted tasks header", () => {
    render(<App />);
    expect(screen.getByText("Submitted tasks")).toBeInTheDocument();
  });
});

describe("App interaction", () => {
  it("switches to Hand world view when toggle is clicked", () => {
    render(<App />);
    const worldButton = screen.getByText("Hand world");
    expect(worldButton).toHaveAttribute("aria-selected", "false");

    fireEvent.click(worldButton);

    expect(worldButton).toHaveAttribute("aria-selected", "true");
    const classicButton = screen.getByText("Classic view");
    expect(classicButton).toHaveAttribute("aria-selected", "false");
  });

  it("switches back to Classic view when toggle is clicked", () => {
    render(<App />);
    // Switch to world first
    fireEvent.click(screen.getByText("Hand world"));
    // Switch back
    fireEvent.click(screen.getByText("Classic view"));

    expect(screen.getByText("Classic view")).toHaveAttribute("aria-selected", "true");
    expect(screen.getByText("Hand world")).toHaveAttribute("aria-selected", "false");
  });

  it("navigates to scheduled tasks view when button is clicked", () => {
    render(<App />);
    const scheduledBtn = screen.getByText("Scheduled tasks");
    fireEvent.click(scheduledBtn);

    // The schedule view should now be active (button gets active class)
    expect(scheduledBtn.className).toContain("active");
  });

  it("navigates back to submission view via New submission button", () => {
    render(<App />);
    // Navigate away first
    fireEvent.click(screen.getByText("Scheduled tasks"));
    // Navigate back
    const newSubmBtn = screen.getByText("New submission");
    fireEvent.click(newSubmBtn);

    // The submission form should be visible (Run button present)
    expect(screen.getByText("Run")).toBeInTheDocument();
  });

  it("opens the Advanced settings panel in the submission form", () => {
    render(<App />);
    const advancedSummary = screen.getByText("Advanced");
    expect(advancedSummary).toBeInTheDocument();

    // Click to expand (details/summary)
    fireEvent.click(advancedSummary);

    // Backend select should be visible after expanding
    const backendLabel = screen.getByText("Backend");
    expect(backendLabel).toBeInTheDocument();
  });

  it("changes the repo path input value", () => {
    render(<App />);
    const repoInput = screen.getByPlaceholderText("owner/repo") as HTMLInputElement;
    fireEvent.change(repoInput, { target: { value: "other/repo" } });
    expect(repoInput.value).toBe("other/repo");
  });

  it("changes the prompt input value", () => {
    render(<App />);
    const promptInput = screen.getByPlaceholderText("Prompt") as HTMLInputElement;
    fireEvent.change(promptInput, { target: { value: "Fix all bugs" } });
    expect(promptInput.value).toBe("Fix all bugs");
  });

  it("changes the backend select value in advanced settings", () => {
    render(<App />);
    // Expand advanced
    fireEvent.click(screen.getByText("Advanced"));

    const backendSelect = screen.getByDisplayValue("claudecodecli") as HTMLSelectElement;
    fireEvent.change(backendSelect, { target: { value: "goose" } });
    expect(backendSelect.value).toBe("goose");
  });

  it("renders Clear button disabled when no task history", () => {
    render(<App />);
    const clearBtn = screen.getByText("Clear");
    expect(clearBtn).toBeDisabled();
  });
});
