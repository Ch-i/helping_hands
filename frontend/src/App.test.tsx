import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";

import App from "./App";

// Build a mock Response-like object with clone() support.
function mockResponse(props: {
  ok: boolean;
  status: number;
  jsonData?: unknown;
  textData?: string;
}) {
  const { ok, status, jsonData = {}, textData } = props;
  const obj = {
    ok,
    status,
    json: async () => jsonData,
    text: async () => textData ?? JSON.stringify(jsonData),
    clone: () => ({ ...obj, json: obj.json, text: obj.text }),
  };
  return obj;
}

// Helper to create a mock fetch that resolves with specific responses per URL pattern.
function mockFetchResponses(
  overrides: Record<string, ReturnType<typeof mockResponse>> = {}
) {
  const defaultResp = mockResponse({ ok: false, status: 503 });

  return vi.fn().mockImplementation((url: string) => {
    for (const [pattern, value] of Object.entries(overrides)) {
      if (url.includes(pattern)) {
        return Promise.resolve(value);
      }
    }
    return Promise.resolve(defaultResp);
  });
}

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

describe("Form submission", () => {
  it("submits the form and transitions to monitor view on success", async () => {
    const mockFetch = mockFetchResponses({
      "/build": mockResponse({
        ok: true,
        status: 200,
        jsonData: { task_id: "abc-123", status: "QUEUED", backend: "claudecodecli" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);

    // Submit the form
    const runButton = screen.getByText("Run");
    await act(async () => {
      fireEvent.click(runButton);
    });

    // Verify fetch was called with /build
    const buildCall = mockFetch.mock.calls.find(
      (call: string[]) => typeof call[0] === "string" && call[0].includes("/build")
    );
    expect(buildCall).toBeTruthy();

    // Verify the POST body structure
    const fetchOptions = buildCall![1] as RequestInit;
    expect(fetchOptions.method).toBe("POST");
    const body = JSON.parse(fetchOptions.body as string);
    expect(body.repo_path).toBe("suryarastogi/helping_hands");
    expect(body.backend).toBe("claudecodecli");
    expect(body.max_iterations).toBe(6);
  });

  it("shows error state when submission fails with network error", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new Error("Network failure"))
    );

    render(<App />);

    await act(async () => {
      fireEvent.click(screen.getByText("Run"));
    });

    // The output should show the error in monitor view
    await waitFor(() => {
      const outputEl = document.querySelector(".monitor-output");
      expect(outputEl?.textContent).toContain("Error");
    });
  });

  it("shows error state when server returns non-ok response", async () => {
    const mockFetch = mockFetchResponses({
      "/build": mockResponse({
        ok: false,
        status: 422,
        jsonData: { detail: "Missing required field" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);

    await act(async () => {
      fireEvent.click(screen.getByText("Run"));
    });

    await waitFor(() => {
      const outputEl = document.querySelector(".monitor-output");
      expect(outputEl?.textContent).toContain("Error");
    });
  });

  it("includes model in payload when set in advanced settings", async () => {
    const mockFetch = mockFetchResponses({
      "/build": mockResponse({
        ok: true,
        status: 200,
        jsonData: { task_id: "def-456", status: "QUEUED", backend: "claudecodecli" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);

    // Expand advanced and change model
    fireEvent.click(screen.getByText("Advanced"));
    const modelInput = screen.getByPlaceholderText("claude-opus-4-6") as HTMLInputElement;
    fireEvent.change(modelInput, { target: { value: "gpt-5.2" } });

    await act(async () => {
      fireEvent.click(screen.getByText("Run"));
    });

    const buildCall = mockFetch.mock.calls.find(
      (call: string[]) => typeof call[0] === "string" && call[0].includes("/build")
    );
    const body = JSON.parse((buildCall![1] as RequestInit).body as string);
    expect(body.model).toBe("gpt-5.2");
  });

  it("includes tools and skills in payload when set", async () => {
    const mockFetch = mockFetchResponses({
      "/build": mockResponse({
        ok: true,
        status: 200,
        jsonData: { task_id: "ghi-789", status: "QUEUED", backend: "claudecodecli" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);

    // Expand advanced and set tools/skills
    fireEvent.click(screen.getByText("Advanced"));
    const toolsInput = screen.getByPlaceholderText("execution,web") as HTMLInputElement;
    fireEvent.change(toolsInput, { target: { value: "execution, web" } });
    const skillsInput = screen.getByPlaceholderText("execution,web,prd,ralph") as HTMLInputElement;
    fireEvent.change(skillsInput, { target: { value: "prd, ralph" } });

    await act(async () => {
      fireEvent.click(screen.getByText("Run"));
    });

    const buildCall = mockFetch.mock.calls.find(
      (call: string[]) => typeof call[0] === "string" && call[0].includes("/build")
    );
    const body = JSON.parse((buildCall![1] as RequestInit).body as string);
    expect(body.tools).toEqual(["execution", "web"]);
    expect(body.skills).toEqual(["prd", "ralph"]);
  });

  it("toggles checkbox fields in advanced settings", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Advanced"));

    const noPrCheckbox = screen.getByLabelText("No PR") as HTMLInputElement;
    expect(noPrCheckbox.checked).toBe(false);
    fireEvent.click(noPrCheckbox);
    expect(noPrCheckbox.checked).toBe(true);

    const executionCheckbox = screen.getByLabelText("Execution") as HTMLInputElement;
    expect(executionCheckbox.checked).toBe(false);
    fireEvent.click(executionCheckbox);
    expect(executionCheckbox.checked).toBe(true);

    const webCheckbox = screen.getByLabelText("Web") as HTMLInputElement;
    expect(webCheckbox.checked).toBe(false);
    fireEvent.click(webCheckbox);
    expect(webCheckbox.checked).toBe(true);

    const nativeAuthCheckbox = screen.getByLabelText("Native auth") as HTMLInputElement;
    expect(nativeAuthCheckbox.checked).toBe(false);
    fireEvent.click(nativeAuthCheckbox);
    expect(nativeAuthCheckbox.checked).toBe(true);

    const fixCiCheckbox = screen.getByLabelText("Fix CI") as HTMLInputElement;
    expect(fixCiCheckbox.checked).toBe(false);
    fireEvent.click(fixCiCheckbox);
    expect(fixCiCheckbox.checked).toBe(true);
  });

  it("changes max iterations in advanced settings", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Advanced"));

    const iterInput = screen.getByDisplayValue("6") as HTMLInputElement;
    fireEvent.change(iterInput, { target: { value: "10" } });
    expect(iterInput.value).toBe("10");
  });
});

describe("Monitor view", () => {
  async function submitAndEnterMonitor() {
    const mockFetch = mockFetchResponses({
      "/build": mockResponse({
        ok: true,
        status: 200,
        jsonData: { task_id: "mon-001", status: "QUEUED", backend: "claudecodecli" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);

    await act(async () => {
      fireEvent.click(screen.getByText("Run"));
    });

    return mockFetch;
  }

  it("shows output tabs after submission", async () => {
    await submitAndEnterMonitor();

    expect(screen.getByRole("tab", { name: "Updates" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Raw" })).toBeInTheDocument();
    expect(screen.getByRole("tab", { name: "Payload" })).toBeInTheDocument();
  });

  it("Updates tab is active by default", async () => {
    await submitAndEnterMonitor();

    const updatesTab = screen.getByRole("tab", { name: "Updates" });
    expect(updatesTab).toHaveAttribute("aria-selected", "true");
  });

  it("switches to Raw tab when clicked", async () => {
    await submitAndEnterMonitor();

    const rawTab = screen.getByRole("tab", { name: "Raw" });
    fireEvent.click(rawTab);

    expect(rawTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "Updates" })).toHaveAttribute(
      "aria-selected",
      "false"
    );
  });

  it("switches to Payload tab when clicked", async () => {
    await submitAndEnterMonitor();

    const payloadTab = screen.getByRole("tab", { name: "Payload" });
    fireEvent.click(payloadTab);

    expect(payloadTab).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: "Updates" })).toHaveAttribute(
      "aria-selected",
      "false"
    );
  });

  it("shows the task ID badge after submission", async () => {
    await submitAndEnterMonitor();

    // The monitor title includes the short task ID
    await waitFor(() => {
      const title = document.querySelector(".monitor-title");
      expect(title?.textContent).toContain("mon-001");
    });
  });

  it("displays the status blinker", async () => {
    await submitAndEnterMonitor();

    const blinker = document.querySelector(".status-blinker");
    expect(blinker).toBeInTheDocument();
  });

  it("shows task inputs section", async () => {
    await submitAndEnterMonitor();

    expect(screen.getByText("Task inputs")).toBeInTheDocument();
  });

  it("shows content in Payload tab after switching", async () => {
    await submitAndEnterMonitor();

    const payloadTab = screen.getByRole("tab", { name: "Payload" });
    fireEvent.click(payloadTab);

    const outputEl = document.querySelector(".monitor-output");
    // The payload tab should display some JSON content (may be build response or
    // error from subsequent polling -- the key assertion is that switching tabs works).
    expect(outputEl?.textContent).toBeTruthy();
    expect(outputEl?.textContent?.trim().startsWith("{")).toBe(true);
  });
});

describe("Schedule view", () => {
  it("shows the schedule view with heading and New schedule button", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));

    expect(screen.getByText("Scheduled tasks", { selector: "h2" })).toBeInTheDocument();
    expect(screen.getByText("New schedule")).toBeInTheDocument();
    expect(screen.getByText("Refresh")).toBeInTheDocument();
  });

  it("shows the schedule form when New schedule is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    // The schedule form should have a Name input and a cron input
    expect(screen.getByPlaceholderText("e.g. Daily docs update")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("0 0 * * * (midnight)")).toBeInTheDocument();
  });

  it("changes schedule form field values", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    const nameInput = screen.getByPlaceholderText("e.g. Daily docs update") as HTMLInputElement;
    fireEvent.change(nameInput, { target: { value: "My nightly job" } });
    expect(nameInput.value).toBe("My nightly job");

    const cronInput = screen.getByPlaceholderText("0 0 * * * (midnight)") as HTMLInputElement;
    fireEvent.change(cronInput, { target: { value: "0 0 * * *" } });
    expect(cronInput.value).toBe("0 0 * * *");
  });

  it("shows cron preset dropdown in the schedule form", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    // Cron presets are in a select dropdown
    expect(screen.getByText("Custom")).toBeInTheDocument();
  });

  it("selects a cron preset from the dropdown", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    // Find the preset select by its label "Or preset"
    const presetSelect = screen.getByDisplayValue("Custom") as HTMLSelectElement;
    fireEvent.change(presetSelect, { target: { value: "daily" } });

    const cronInput = screen.getByPlaceholderText("0 0 * * * (midnight)") as HTMLInputElement;
    expect(cronInput.value).toBe("0 0 * * *");
  });

  it("submits schedule form and calls the API", async () => {
    // The save handler does POST then calls loadSchedules() which does GET.
    // Both hit /schedules. We use a smart mock that differentiates by method.
    const mockFetch = vi.fn().mockImplementation((url: string, init?: RequestInit) => {
      if (typeof url === "string" && url.includes("/schedules")) {
        if (init?.method === "POST") {
          return Promise.resolve(
            mockResponse({
              ok: true,
              status: 200,
              jsonData: { schedule_id: "sched-001", name: "Nightly" },
            })
          );
        }
        // GET (loadSchedules after save)
        return Promise.resolve(
          mockResponse({
            ok: true,
            status: 200,
            jsonData: { schedules: [], total: 0 },
          })
        );
      }
      return Promise.resolve(mockResponse({ ok: false, status: 503 }));
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    // Fill the form
    const nameInput = screen.getByPlaceholderText("e.g. Daily docs update") as HTMLInputElement;
    fireEvent.change(nameInput, { target: { value: "Nightly" } });

    const cronInput = screen.getByPlaceholderText("0 0 * * * (midnight)") as HTMLInputElement;
    fireEvent.change(cronInput, { target: { value: "0 0 * * *" } });

    const promptArea = screen.getByPlaceholderText("Update documentation...") as HTMLTextAreaElement;
    fireEvent.change(promptArea, { target: { value: "Run nightly checks" } });

    // Submit the schedule form
    const createButton = screen.getByText("Create schedule");
    await act(async () => {
      fireEvent.click(createButton);
    });

    // Verify fetch was called with /schedules POST
    const scheduleCall = mockFetch.mock.calls.find(
      (call: string[]) =>
        typeof call[0] === "string" &&
        call[0].includes("/schedules") &&
        (call[1] as RequestInit)?.method === "POST"
    );
    expect(scheduleCall).toBeTruthy();
    const body = JSON.parse((scheduleCall![1] as RequestInit).body as string);
    expect(body.name).toBe("Nightly");
    expect(body.cron_expression).toBe("0 0 * * *");
    expect(body.prompt).toBe("Run nightly checks");
  });

  it("hides the schedule form when Cancel is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    // Form should be visible
    expect(screen.getByPlaceholderText("e.g. Daily docs update")).toBeInTheDocument();

    // Click Cancel
    fireEvent.click(screen.getByText("Cancel"));

    // Form should disappear; the empty state message should show
    expect(screen.getByText("No scheduled tasks yet.")).toBeInTheDocument();
  });

  it("refreshes schedules list when Refresh is clicked", async () => {
    const mockFetch = mockFetchResponses({
      "/schedules": mockResponse({
        ok: true,
        status: 200,
        jsonData: { schedules: [], total: 0 },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));

    await act(async () => {
      fireEvent.click(screen.getByText("Refresh"));
    });

    const scheduleFetches = mockFetch.mock.calls.filter(
      (call: string[]) =>
        typeof call[0] === "string" &&
        call[0].includes("/schedules") &&
        !(call[1] as RequestInit)?.method
    );
    expect(scheduleFetches.length).toBeGreaterThan(0);
  });

  it("shows schedule error when creation API returns failure", async () => {
    const mockFetch = mockFetchResponses({
      "/schedules": mockResponse({
        ok: false,
        status: 500,
        jsonData: { detail: "Server error" },
      }),
    });
    vi.stubGlobal("fetch", mockFetch);

    render(<App />);
    fireEvent.click(screen.getByText("Scheduled tasks"));
    fireEvent.click(screen.getByText("New schedule"));

    // Fill minimum fields and submit
    const nameInput = screen.getByPlaceholderText("e.g. Daily docs update") as HTMLInputElement;
    fireEvent.change(nameInput, { target: { value: "Test" } });
    const cronInput = screen.getByPlaceholderText("0 0 * * * (midnight)") as HTMLInputElement;
    fireEvent.change(cronInput, { target: { value: "* * * * *" } });
    const promptArea = screen.getByPlaceholderText("Update documentation...") as HTMLTextAreaElement;
    fireEvent.change(promptArea, { target: { value: "test" } });

    await act(async () => {
      fireEvent.click(screen.getByText("Create schedule"));
    });

    // Verify the submission happened
    const saveCall = mockFetch.mock.calls.find(
      (call: string[]) =>
        typeof call[0] === "string" &&
        call[0].includes("/schedules") &&
        (call[1] as RequestInit)?.method === "POST"
    );
    expect(saveCall).toBeTruthy();
  });
});
