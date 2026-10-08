// Public Pages gateway for the isolated ad-commerce Sandbox Worker.
// The Service Binding stays inside Cloudflare and does not duplicate PayPal secrets.
export default {
  async fetch(request, env) {
    return env.SANDBOX.fetch(request);
  }
};
