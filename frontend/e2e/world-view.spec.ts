import { test, expect } from "@playwright/test";
import { mockApiRoutes } from "./helpers";

test.beforeEach(async ({ page }) => {
  await mockApiRoutes(page);
});

test("switching to world view shows Hand Office", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: "Hand world" }).click();
  await expect(page.getByText("Hand Office")).toBeVisible();
});

test("world view shows office scene with desks and player", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: "Hand world" }).click();

  await expect(page.locator(".world-scene")).toBeVisible();
  await expect(page.locator(".office-desk").first()).toBeVisible();
  await expect(page.locator(".human-player")).toBeVisible();
});

test("world view shows office status summary", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: "Hand world" }).click();

  await expect(page.getByText("Office Status")).toBeVisible();
  await expect(page.locator(".office-status-summary").getByText("8 Desks")).toBeVisible();
  await expect(page.getByText("Use arrow keys to walk")).toBeVisible();
});

test("switching back to classic view hides the office", async ({ page }) => {
  await page.goto("/");
  // Go to world view
  await page.getByRole("tab", { name: "Hand world" }).click();
  await expect(page.getByText("Hand Office")).toBeVisible();

  // Go back to classic
  await page.getByRole("tab", { name: "Classic view" }).click();
  await expect(page.getByText("Hand Office")).not.toBeVisible();
  await expect(page.locator("input.repo-input")).toBeVisible();
});

test("world view submission card appears below the office", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: "Hand world" }).click();

  // In world view, the submission/monitor card is shown below the office scene
  await expect(page.locator(".hand-world-card")).toBeVisible();
});

test("Claude usage panel is visible in world view", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("tab", { name: "Hand world" }).click();

  await expect(page.getByText("Claude Usage")).toBeVisible();
});
