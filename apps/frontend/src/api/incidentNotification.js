import { adminClient } from "./adminClient";

export function getTemplates() {
  return adminClient.get("/admin/incident-notification/templates");
}

export function sendNotification(payload) {
  return adminClient.post("/admin/incident-notification/send", payload);
}
