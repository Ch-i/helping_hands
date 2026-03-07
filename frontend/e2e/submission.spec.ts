import { test, expect } from "@playwright/test";
import { mockApiRoutes } from "./helpers";

test.beforeEach(async ({ page }) => {
  await mockApiRoutes(page);
});

test("submission form has required fields", async ({ page }) => {
  await page.goto("/");
  const repoInput = page.locator("input.repo-input");
  const promptInput = page.locator("input.prompt-input");
  const submitBtn = page.locator("button.submit-inline");

  await expect(repoInput).toBeVisible();
  await expect(promptInput).toBeVisible();
  await expect(submitBtn).toBeVisible();
});

test("advanced settings expand on click", async ({ page }) => {
  await page.goto("/");
  const details = page.locator("details.compact-advanced");
  // Initially collapsed — backend select not visible
  await expect(details.locator("select")).not.toBeVisible();
  // Expand
  await details.locator("summary").click();
  await expect(details.locator("select").first()).toBeVisible();
});

test("submitting a run navigates to monitor view", async ({ page }) => {
  // Mock the build endpoint
  await page.route("**/build", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "test-task-123",
        status: "PENDING",
        backend: "e2e",
      }),
    }),
  );
  // Mock task polling
  await page.route("**/tasks/test-task-123*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        task_id: "test-task-123",
        status: "STARTED",
        result: null,
      }),
    }),
  );
  await mockApiRoutes(page);

  await page.goto("/");
  await page.locator("input.repo-input").fill("owner/repo");
  await page.locator("input.prompt-input").fill("Fix the bug");
  await page.locator("button.submit-inline").click();

  // Should switch to monitor view and show the task
  await expect(page.locator(".monitor-title")).toBeVisible();
});

test("repo input has required attribute", async ({ page }) => {
  await page.goto("/");
  const repoInput = page.locator("input.repo-input");
  await expect(repoInput).toHaveAttribute("required", "");
});

test("prompt input has required attribute", async ({ page }) => {
  await page.goto("/");
  const promptInput = page.locator("input.prompt-input");
  await expect(promptInput).toHaveAttribute("required", "");
});
