import { type Page } from "@playwright/test";

/** Mock every backend API route so the frontend can render without a real server. */
export async function mockApiRoutes(page: Page) {
  await page.route("**/health/services", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        status: "ok",
        redis: "ok",
        db: "na",
        workers: "ok",
      }),
    }),
  );

  await page.route("**/workers/capacity*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ max_workers: 4, source: "env", workers: {} }),
    }),
  );

  await page.route("**/tasks/current*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ tasks: [], source: "celery" }),
    }),
  );

  await page.route("**/config", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ in_docker: false, native_auth_default: false }),
    }),
  );

  await page.route("**/schedules", (route) => {
    if (route.request().method() === "GET") {
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ schedules: [], total: 0 }),
      });
    }
    // POST — create schedule
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ id: "sched-1", name: "Test Schedule" }),
    });
  });

  await page.route("**/schedules/*", (route) => {
    if (route.request().method() === "DELETE") {
      return route.fulfill({ status: 204, body: "" });
    }
    // PUT — update
    return route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ id: "sched-1", name: "Updated" }),
    });
  });

  await page.route("**/health/claude-usage*", (route) =>
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        levels: [
          { name: "Daily", percent_used: 42 },
          { name: "Weekly", percent_used: 18 },
        ],
      }),
    }),
  );
}
