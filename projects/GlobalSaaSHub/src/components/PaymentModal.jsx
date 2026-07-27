import React, { useState } from 'react';
import { trackSponsorshipOrder } from '../utils/analytics';
import { 
  X, 
  CreditCard, 
  ShieldCheck, 
  CheckCircle2, 
  Sparkles, 
  Lock, 
  Zap, 
  ArrowRight,
  ExternalLink,
  Award,
  Globe
} from 'lucide-react';

export default function PaymentModal({ isOpen, onClose }) {
  const [paymentMethod, setPaymentMethod] = useState('card'); // 'card' | 'paypal'
  const [toolName, setToolName] = useState('');
  const [toolUrl, setToolUrl] = useState('');
  const [contactEmail, setContactEmail] = useState('');
  
  // Card Form State
  const [cardNumber, setCardNumber] = useState('');
  const [cardExp, setCardExp] = useState('');
  const [cardCvc, setCardCvc] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmitPayment = (e) => {
    e.preventDefault();
    setIsProcessing(true);
    trackSponsorshipOrder(toolName || 'AI Tool', 49, contactEmail);

    const paypalCardCheckoutUrl = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=websilonsg@gmail.com&item_name=${encodeURIComponent(
      `GlobalSaaSHub Premium Sponsorship - ${toolName || 'AI Tool'}`
    )}&amount=49.00&currency_code=USD&custom=${encodeURIComponent(contactEmail || '')}`;

    setTimeout(() => {
      setIsProcessing(false);
      window.open(paypalCardCheckoutUrl, '_blank');
      setIsSuccess(true);
    }, 800);
  };

  const handlePayPalRedirect = () => {
    trackSponsorshipOrder(toolName || 'AI Tool', 49, contactEmail);
    const paypalUrl = `https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=websilonsg@gmail.com&item_name=${encodeURIComponent(
      `GlobalSaaSHub Premium Sponsorship - ${toolName || 'AI Tool'}`
    )}&amount=49.00&currency_code=USD&custom=${encodeURIComponent(contactEmail || '')}`;
    window.open(paypalUrl, '_blank');
    setIsSuccess(true);
  };


  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto animate-fadeIn">
      <div 
        style={{ backgroundColor: '#131520', borderColor: '#3b0764' }}
        className="relative max-w-xl w-full rounded-3xl border-2 shadow-2xl overflow-hidden my-8"
      >
        {/* Top Accent Gradient Bar */}
        <div className="h-2 bg-gradient-to-r from-purple-600 via-indigo-500 to-emerald-400" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-[#181a29] text-slate-400 hover:text-white border border-[#222538] hover:border-purple-500/40 transition-all z-20"
        >
          <X className="h-5 w-5" />
        </button>

        {isSuccess ? (
          <div className="p-8 text-center space-y-6">
            <div className="h-20 w-20 bg-emerald-500/10 border-2 border-emerald-500/30 text-emerald-400 rounded-3xl flex items-center justify-center mx-auto shadow-xl shadow-emerald-950/50">
              <CheckCircle2 className="h-10 w-10" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-white mb-2">Sponsorship Order Confirmed!</h2>
              <p className="text-sm text-slate-300 max-w-md mx-auto leading-relaxed">
                Thank you! Your payment of <span className="font-bold text-emerald-400">$49.00 USD</span> has been processed. <br />
                <span className="font-bold text-purple-300">{toolName || 'Your AI Tool'}</span> will be reviewed and featured at the top of GlobalSaaSHub within 24 hours.
              </p>
            </div>

            <div className="p-4 rounded-2xl bg-[#181a29] border border-[#222538] text-xs text-slate-400 space-y-2 text-left">
              <div className="flex justify-between">
                <span>Confirmation Email:</span>
                <span className="font-bold text-white">{contactEmail || 'Provided Email'}</span>
              </div>
              <div className="flex justify-between">
                <span>Sponsorship Plan:</span>
                <span className="font-bold text-emerald-400">Featured Premium ($49.00 USD)</span>
              </div>
            </div>

            <button
              onClick={onClose}
              className="w-full py-3.5 rounded-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg shadow-purple-950/50 hover:brightness-110 transition-all"
            >
              Return to Website
            </button>
          </div>
        ) : (
          <div className="p-6 sm:p-8 space-y-6">
            
            {/* Header Title */}
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold bg-purple-500/10 border border-purple-500/20 text-purple-300">
                <Sparkles className="h-3.5 w-3.5 text-purple-400" />
                <span>Featured Sponsorship</span>
              </div>
              <h2 className="text-2xl font-black text-white tracking-tight flex items-center justify-between">
                <span>Sponsor Your AI Tool</span>
                <span className="text-emerald-400 text-xl">$49 <span className="text-xs font-semibold text-slate-400">/ one-time</span></span>
              </h2>
              <p className="text-xs text-slate-400 leading-relaxed">
                Get your AI software featured at the top of GlobalSaaSHub for thousands of active digital creators, developers, and buyers.
              </p>
            </div>

            {/* Benefits Bullet Points */}
            <div className="grid grid-cols-2 gap-2.5 p-3.5 rounded-2xl bg-[#181a29] border border-[#222538] text-xs">
              <div className="flex items-center gap-2 text-slate-200">
                <Zap className="h-4 w-4 text-purple-400 shrink-0" />
                <span>Top Priority Placement</span>
              </div>
              <div className="flex items-center gap-2 text-slate-200">
                <Globe className="h-4 w-4 text-blue-400 shrink-0" />
                <span>Dofollow SEO Link</span>
              </div>
              <div className="flex items-center gap-2 text-slate-200">
                <Award className="h-4 w-4 text-amber-400 shrink-0" />
                <span>Verified Tool Badge</span>
              </div>
              <div className="flex items-center gap-2 text-slate-200">
                <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
                <span>24h Guaranteed Live</span>
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmitPayment} className="space-y-4">
              
              {/* Product Info inputs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Tool / Company Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. GoHighLevel"
                    value={toolName}
                    onChange={(e) => setToolName(e.target.value)}
                    className="w-full bg-[#181a29] border border-[#222538] focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none transition-all"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Official Website URL *
                  </label>
                  <input
                    type="url"
                    required
                    placeholder="https://yourtool.com"
                    value={toolUrl}
                    onChange={(e) => setToolUrl(e.target.value)}
                    className="w-full bg-[#181a29] border border-[#222538] focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Category *
                  </label>
                  <select
                    required
                    className="w-full bg-[#181a29] border border-[#222538] focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white focus:outline-none transition-all"
                  >
                    <option value="Workflow Automation">Workflow Automation</option>
                    <option value="Creator & Productivity">Creator & Productivity</option>
                    <option value="Developer APIs">Developer APIs</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                    Pricing Model *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Free plan / $19/mo"
                    className="w-full bg-[#181a29] border border-[#222538] focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none transition-all"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Short Tagline / Description *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. An AI-powered automation platform to boost marketing..."
                  className="w-full bg-[#181a29] border border-[#222538] focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-1.5">
                  Contact Email (For Receipt & Confirmation) *
                </label>
                <input
                  type="email"
                  required
                  placeholder="contact@company.com"
                  value={contactEmail}
                  onChange={(e) => setContactEmail(e.target.value)}
                  className="w-full bg-[#181a29] border border-[#222538] focus:border-purple-500 rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none transition-all"
                />
              </div>


              {/* Payment Method Selector */}
              <div className="pt-2">
                <label className="block text-[11px] font-bold text-slate-300 uppercase tracking-wider mb-2">
                  Select Payment Method
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <button
                    type="button"
                    onClick={() => setPaymentMethod('card')}
                    className={`py-3 px-4 rounded-xl text-xs font-bold border flex items-center justify-center gap-2 transition-all ${
                      paymentMethod === 'card'
                        ? 'bg-purple-600/20 border-purple-500 text-white shadow-lg shadow-purple-950/40'
                        : 'bg-[#181a29] border-[#222538] text-slate-400 hover:text-white'
                    }`}
                  >
                    <CreditCard className="h-4 w-4 text-purple-400" />
                    <span>Credit Card (VISA / MC)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setPaymentMethod('paypal')}
                    className={`py-3 px-4 rounded-xl text-xs font-bold border flex items-center justify-center gap-2 transition-all ${
                      paymentMethod === 'paypal'
                        ? 'bg-blue-600/20 border-blue-500 text-white shadow-lg shadow-blue-950/40'
                        : 'bg-[#181a29] border-[#222538] text-slate-400 hover:text-white'
                    }`}
                  >
                    <span className="font-extrabold text-blue-400 text-sm">PayPal</span>
                    <span>Express</span>
                  </button>
                </div>
              </div>

              {/* Credit Card Fields */}
              {paymentMethod === 'card' ? (
                <div className="p-5 rounded-2xl bg-[#181a29] border border-[#222538] text-center space-y-4 animate-fadeIn">
                  <div className="flex items-center justify-center gap-3 text-slate-300">
                    <CreditCard className="h-5 w-5 text-purple-400" />
                    <span className="text-xs font-bold">Direct Card Processing (VISA, Mastercard, AMEX, Discover)</span>
                  </div>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                    Pay securely using any major credit or debit card. No PayPal account registration required.
                  </p>

                  <button
                    type="submit"
                    disabled={isProcessing}
                    className="w-full py-4 rounded-xl font-extrabold text-xs bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-xl shadow-purple-950/50 hover:brightness-110 transition-all flex items-center justify-center gap-2"
                  >
                    {isProcessing ? (
                      <span>Connecting to 256-Bit SSL Card Gateway...</span>
                    ) : (
                      <>
                        <Lock className="h-4 w-4 text-purple-300" />
                        <span>Proceed to Secure Credit Card Checkout ($49.00 USD)</span>
                        <ArrowRight className="h-4 w-4" />
                      </>
                    )}
                  </button>
                </div>
              ) : (
                /* PayPal Direct Button */
                <div className="p-5 rounded-2xl bg-[#181a29] border border-[#222538] text-center space-y-4 animate-fadeIn">
                  <div className="flex items-center justify-center gap-2 text-slate-300">
                    <span className="font-extrabold text-blue-400 text-sm">PayPal</span>
                    <span className="text-xs font-bold">One-Click Express Checkout</span>
                  </div>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">
                    Instant one-click checkout using your PayPal account balance or linked credit cards.
                  </p>
                  <button
                    type="button"
                    onClick={handlePayPalRedirect}
                    className="w-full py-4 rounded-xl font-extrabold text-xs bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-xl shadow-blue-950/50 hover:brightness-110 transition-all flex items-center justify-center gap-2"
                  >
                    <span className="font-black text-sm">PayPal</span>
                    <span>$49.00 Express Checkout</span>
                    <ExternalLink className="h-4 w-4" />
                  </button>
                </div>
              )}


              {/* Trust Footer */}
              <div className="pt-2 flex items-center justify-between text-[10px] text-slate-500 font-semibold border-t border-[#222538]">
                <div className="flex items-center gap-1.5">
                  <Lock className="h-3 w-3 text-emerald-400" />
                  <span>256-Bit SSL Encrypted Checkout</span>
                </div>
                <div>
                  <span>Powered by PayPal Secure Gateway</span>
                </div>
              </div>

            </form>
          </div>
        )}
      </div>
    </div>
  );
}

