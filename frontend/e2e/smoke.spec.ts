import { test, expect } from "@playwright/test";
import { mockApiRoutes } from "./helpers";

test.beforeEach(async ({ page }) => {
  await mockApiRoutes(page);
});

test("app renders with title", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveTitle("helping_hands runner");
});

test("sidebar buttons are visible", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("button", { name: "New submission" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Scheduled tasks" })).toBeVisible();
});

test("view toggle tabs are visible", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("tab", { name: "Classic view" })).toBeVisible();
  await expect(page.getByRole("tab", { name: "Hand world" })).toBeVisible();
});

test("clicking Scheduled tasks switches to schedule view", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Scheduled tasks" }).click();
  await expect(page.getByText("Create and manage recurring builds.")).toBeVisible();
});

test("clicking New submission shows the form", async ({ page }) => {
  await page.goto("/");
  // Navigate away first
  await page.getByRole("button", { name: "Scheduled tasks" }).click();
  await expect(page.getByText("Create and manage recurring builds.")).toBeVisible();
  // Navigate back
  await page.getByRole("button", { name: "New submission" }).click();
  await expect(page.locator("input.repo-input")).toBeVisible();
});

test("service health bar renders", async ({ page }) => {
  await page.goto("/");
  await expect(page.locator("[aria-label='Service health']")).toBeVisible();
});
