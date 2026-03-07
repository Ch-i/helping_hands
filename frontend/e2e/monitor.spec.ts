import { test, expect } from "@playwright/test";
import { mockApiRoutes } from "./helpers";

test.beforeEach(async ({ page }) => {
  await mockApiRoutes(page);
});

test("monitor view shows output tabs", async ({ page }) => {
  await page.route("**/build", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-abc",
        status: "PENDING",
        backend: "e2e",
      }),
    }),
  );
  await page.route("**/tasks/task-abc*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-abc",
        status: "STARTED",
        result: { updates: ["Step 1 done", "Step 2 done"] },
      }),
    }),
  );

  await page.goto("/");
  await page.locator("input.repo-input").fill("owner/repo");
  await page.locator("input.prompt-input").fill("Do something");
  await page.locator("button.submit-inline").click();

  // Output tabs should appear
  await expect(page.getByRole("tab", { name: "Updates" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Raw" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Payload" })).toBeVisible();
});

test("task appears in sidebar after submission", async ({ page }) => {
  await page.route("**/build", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-xyz-1234",
        status: "PENDING",
        backend: "claudecodecli",
      }),
    }),
  );
  await page.route("**/tasks/task-xyz-1234*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-xyz-1234",
        status: "STARTED",
        result: null,
      }),
    }),
  );

  await page.goto("/");
  await page.locator("input.repo-input").fill("owner/repo");
  await page.locator("input.prompt-input").fill("Build feature");
  await page.locator("button.submit-inline").click();

  // The task ID (short form) should appear in the sidebar task list
  await expect(page.locator(".task-list")).toBeVisible();
});

test("clicking a task in the sidebar selects it", async ({ page }) => {
  // Pre-populate with a completed task via monitor flow
  await page.route("**/build", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-select-test",
        status: "PENDING",
        backend: "e2e",
      }),
    }),
  );
  await page.route("**/tasks/task-select-test*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "task-select-test",
        status: "SUCCESS",
        result: { summary: "All done" },
      }),
    }),
  );

  await page.goto("/");
  await page.locator("input.repo-input").fill("owner/repo");
  await page.locator("input.prompt-input").fill("Test");
  await page.locator("button.submit-inline").click();

  // Wait for task to appear
  await expect(page.locator(".task-list")).toBeVisible();

  // Click New submission to go back to form
  await page.getByRole("button", { name: "New submission" }).click();
  await expect(page.locator("input.repo-input")).toBeVisible();

  // Click the task in sidebar
  await page.locator(".task-row").first().click();

  // Should switch to monitor view
  await expect(page.locator(".monitor-title")).toBeVisible();
});
