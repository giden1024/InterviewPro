import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const TermsOfUsePage: React.FC = () => {
  const navigate = useNavigate();

  // 在组件挂载时滚动到页面顶部
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back button */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-600 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            ← Back
          </button>
        </div>

        {/* Terms of use content */}
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-8">
            <div className="prose max-w-none">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">Terms of Use</h1>
              <p className="text-sm text-gray-600 mb-8">Last Updated: June 15, 2025</p>
              
              <p className="text-gray-700 leading-relaxed mb-6">
                Welcome to OfferOtter, an AI-powered interview preparation platform. These Terms of Use ("Terms") govern your access to and use of the OfferOtter website, services, and other offerings (collectively, "Services"). These Terms, together with our Privacy Policy, constitute a legally binding agreement between you ("User" or "you") and OfferOtter ("we," "us," "our"). Please read these Terms carefully before using our Services.
              </p>

              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
                  <p className="text-gray-700">
                    By accessing or using our Services, you agree to be bound by these Terms. If you do not agree to these Terms, you may not access or use our Services.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Eligibility</h2>
                  <p className="text-gray-700">
                    You must be at least 13 years old to use our Services. If you are under 18, you must have your parent or legal guardian's permission to use our Services.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Description of Service</h2>
                  <p className="text-gray-700 mb-2">
                    3.1 OfferOtter provides AI-powered interview preparation services, including but not limited to generating interview questions, simulating interview practice, and real-time interview reminders.
                  </p>
                  <p className="text-gray-700">
                    3.2 You understand and agree that the Services will be updated over time, and paid features may be introduced or modified.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">4. User Accounts</h2>
                  <div className="space-y-2 text-gray-700">
                    <p>4.1 To use certain features of our Services, you may be required to create an account. You agree to provide accurate, current, and complete information during the registration process.</p>
                    <p>4.2 You are responsible for maintaining the confidentiality of your account and password. You agree to accept responsibility for all activities that occur under your account.</p>
                    <p>4.3 You should ensure that the information you submit when using the Services is true, accurate, complete, and up-to-date. When using your account, you must comply with relevant laws and regulations and should not engage in any acts that infringe upon national interests or damage the legal rights and interests of us or any others.</p>
                    <p>4.4 We reserve the right to review your account information if we identify risks and may, depending on the severity of the situation, temporarily suspend, delay, stop, or terminate the provision of some or all services.</p>
                  </div>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">5. User Conduct</h2>
                  <p className="text-gray-700">
                    You agree to use our Services only for purposes that are permitted by these Terms and any applicable law, regulation, or generally accepted practices or guidelines in the relevant jurisdictions.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">6. User Content</h2>
                  <div className="space-y-2 text-gray-700">
                    <p>6.1 You retain all rights to any content you submit, upload, or display through the Services ("User Content").</p>
                    <p>6.2 By submitting, posting, or displaying User Content, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, adapt, publish, translate, and distribute such content in connection with providing and promoting our Services.</p>
                  </div>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Intellectual Property</h2>
                  <div className="space-y-2 text-gray-700">
                    <p>7.1 The Services and their original content, features, and functionality are and will remain the exclusive property of OfferOtter and its licensors.</p>
                    <p>7.2 You may not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on our Services, except as incidental to normal use of the Services.</p>
                  </div>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Privacy and Data Security</h2>
                  <div className="space-y-2 text-gray-700">
                    <p>8.1 Your use of the Services is subject to our Privacy Policy. By using the Services, you acknowledge and agree that you have read and understand our Privacy Policy.</p>
                    <p>8.2 We are committed to protecting your personal information and implement reasonable security measures to safeguard your data.</p>
                  </div>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Subscriptions and Payments</h2>
                  <div className="space-y-2 text-gray-700">
                    <p><strong>9.1 Subscriptions:</strong> All subscriptions to our Services, including renewals, are non-refundable. Once a subscription fee has been paid, no refunds will be provided, regardless of the reason for cancellation or termination. By purchasing a subscription, you acknowledge and agree to this non-refundability policy.</p>
                    <p><strong>9.2 Cancellation Policy:</strong> You may cancel your subscription at any time by accessing your account settings on our website or by contacting us. Cancellations will take effect at the end of the current billing period. You will continue to have access to the Services until the end of your subscription term. Please note that no refunds or credits will be provided for partial subscription periods, including when the subscription is canceled before the end of a billing period.</p>
                    <p><strong>9.3 Automatic Renewal:</strong> All subscriptions will automatically renew at the end of the subscription term unless canceled by the user. By agreeing to these Terms, you authorize OfferOtter to charge the applicable subscription fees for the renewal period.</p>
                  </div>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Disclaimer of Warranties</h2>
                  <p className="text-gray-700">
                    The services are provided on an "as is" and "as available" basis. OfferOtter expressly disclaims all warranties of any kind, whether express or implied, including but not limited to the implied warranties of merchantability, fitness for a particular purpose, and non-infringement.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">11. Limitation of Liability</h2>
                  <p className="text-gray-700">
                    To the maximum extent permitted by law, OfferOtter shall not be liable for any indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly, or any loss of data, use, goodwill, or other intangible losses resulting from your access to or use of or inability to access or use the services.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">12. Indemnification</h2>
                  <p className="text-gray-700">
                    You agree to indemnify and hold OfferOtter harmless from any claims, losses, or damages, including legal fees, resulting from your violation of these Terms, your use of the Services, or your violation of any rights of a third party.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">13. Termination</h2>
                  <p className="text-gray-700">
                    We reserve the right to terminate or suspend your access to all or part of the Services, without prior notice or liability, for any reason whatsoever, including without limitation if you breach these Terms.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">14. Changes to Terms</h2>
                  <p className="text-gray-700">
                    We may modify these Terms at any time. We will post the most current version on our website and, if the changes are significant, we will provide a more prominent notice. Your continued use of the Services after the changes become effective constitutes your acceptance of the new Terms.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">15. Third-Party Services</h2>
                  <p className="text-gray-700">
                    Our Services may contain links to third-party websites or services that are not owned or controlled by OfferOtter. We have no control over, and assume no responsibility for, the content, privacy policies, or practices of any third-party websites or services.
                  </p>
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">16. Contact Information</h2>
                  <p className="text-gray-700">
                    If you have any questions about these Terms, please contact us at: <a href="mailto:support@offerott.com" className="text-indigo-600 hover:text-indigo-800">support@offerott.com</a>
                  </p>
                </div>

                <div className="bg-indigo-50 p-4 rounded-lg">
                  <p className="text-gray-700 font-medium">
                    By using our Services, you acknowledge that you have read, understood, and agree to be bound by these Terms of Use.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsOfUsePage;
