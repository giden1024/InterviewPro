import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const PrivacyPolicyPage: React.FC = () => {
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

        {/* Privacy policy content */}
        <div className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-8">
            <div className="prose max-w-none">
              <h1 className="text-3xl font-bold text-gray-900 mb-6">Privacy Policy</h1>
              <p className="text-sm text-gray-600 mb-8">Last Updated: June 15, 2025</p>

              <div className="space-y-6">
                <p className="text-gray-700 leading-relaxed">
                  OfferOtter ("we", "us", or "our") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website, services, and interview simulation tools (collectively, "Services"). By accessing or using our Services, you consent to the practices described herein. If you do not agree, please discontinue use immediately.
                </p>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Information We Collect</h2>
                  <p className="text-gray-700 mb-3">We collect the following information when you use our Services:</p>
                  
                  <div className="ml-4 space-y-3">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">1.1 Personal Information You Provide:</h3>
                      <ul className="list-disc ml-6 space-y-1 text-gray-700">
                        <li><strong>Account Registration:</strong> When you register or log in (directly or via Facebook/Google), we collect your name, email address, and authentication tokens.</li>
                        <li><strong>Profile Data:</strong> When using our interview tools, we collect your resume, cover letter, job goals, employment history, job descriptions, and any other materials you upload.</li>
                        <li><strong>Audio/Video Data:</strong> During simulated interviews, we process your microphone and camera inputs to provide real-time feedback. Recordings are stored only with your explicit consent and deleted after 7 days.</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">1.2 Automatically Collected Data:</h3>
                      <ul className="list-disc ml-6 space-y-1 text-gray-700">
                        <li><strong>Usage Data:</strong> IP address, browser type, device information, pages visited, session duration, and interaction logs.</li>
                      </ul>
                    </div>
                  </div>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">2. How We Use Your Information</h2>
                  <p className="text-gray-700 mb-3">We process your data for:</p>
                  <ul className="list-disc ml-6 space-y-1 text-gray-700">
                    <li><strong>Service Delivery:</strong> To create accounts, analyze resumes, conduct mock interviews, and generate feedback.</li>
                    <li><strong>Improvements:</strong> To optimize AI algorithms, personalize interview scenarios, and enhance user experience.</li>
                    <li><strong>Communication:</strong> To send service-related announcements (e.g., feature updates).</li>
                    <li><strong>Security:</strong> To prevent fraud, enforce terms, and protect system integrity.</li>
                    <li><strong>Legal Compliance:</strong> To meet regulatory obligations or respond to lawful requests.</li>
                  </ul>
                  <p className="text-gray-700 mt-3">
                    <strong>Legal Basis (GDPR):</strong> Processing relies on your consent (e.g., for recordings), contractual necessity (e.g., account creation), and legitimate interests (e.g., security).
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">3. How We Share Your Information</h2>
                  <p className="text-gray-700 mb-3">We do not sell your data. Disclosures are limited to:</p>
                  <ul className="list-disc ml-6 space-y-1 text-gray-700">
                    <li><strong>Service Providers:</strong> Trusted partners (e.g., cloud storage, analytics) who assist under strict confidentiality.</li>
                    <li><strong>Legal Requirements:</strong> If compelled by law enforcement or legal process.</li>
                    <li><strong>Business Transfers:</strong> In mergers, acquisitions, or asset sales (you will be notified).</li>
                    <li><strong>Anonymized Data:</strong> Aggregate insights (e.g., "60% of users improved interview skills") may be shared.</li>
                  </ul>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Data Security</h2>
                  <p className="text-gray-700">
                    We implement SSL encryption, access controls, and regular audits. Video/audio data is encrypted at rest and in transit. However, no system is 100% secure—promptly report vulnerabilities to support@offerott.com.
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Your Rights</h2>
                  <p className="text-gray-700">
                    You may access, correct, or delete your data, withdraw consent (e.g., disable camera access), opt out of non-essential cookies. Please submit requests to support@offerott.com, we respond within 7 days.
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Third-Party Logins</h2>
                  <p className="text-gray-700">
                    Using Facebook/Google grants us your email and public profile data. We do not access your social media contacts or posts. Manage permissions via your social account settings.
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Children's Privacy</h2>
                  <p className="text-gray-700">
                    You must be at least 13 years old to use our Services. If you are under 18, you must have your parent or legal guardian's permission to use our Services.
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Changes to This Policy</h2>
                  <p className="text-gray-700">
                    We update this policy periodically. Material changes will be notified via email or website alerts. Continued use implies acceptance.
                  </p>
                </section>

                <section>
                  <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Contact Us</h2>
                  <p className="text-gray-700">
                    You can contact us through email: <a href="mailto:support@offerott.com" className="text-indigo-600 hover:text-indigo-800">support@offerott.com</a>
                  </p>
                  <p className="text-gray-700 mt-2">OfferOtter Team</p>
                </section>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
