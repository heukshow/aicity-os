import worker from './index.js';
import { runCampaignMaintenance } from './campaign-automation.js';

export default {
  fetch: worker.fetch,

  async scheduled(controller, env, ctx) {
    if (!env.ORDERS) return;
    const scheduledAt = Number.isFinite(controller?.scheduledTime)
      ? new Date(controller.scheduledTime).toISOString()
      : new Date().toISOString();
    ctx.waitUntil(runCampaignMaintenance(env.ORDERS, scheduledAt));
  },
};
