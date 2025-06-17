import React, { useState } from 'react';
import { OfferotterHomeProps, CoreFeature, Statistic, Testimonial, FAQItem } from './types';

// SVG 图标组件
const LogoIcon: React.FC<{ className?: string }> = ({ className = "w-8 h-8" }) => (
  <svg className={className} viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
    <path d="M1.90678 32.0955Q-2.49299 40.0703 3.25942 46.1745C5.38012 48.4249 8.39583 49.5156 11.4351 50.0851Q32.142 53.9657 42.0702 49.8891Q50.1668 46.5646 50.8877 39.2518C51.2649 35.426 49.3508 31.8566 47.1989 28.6709L45.2818 25.833C44.9067 25.2776 44.9594 24.5559 45.3193 23.9904Q47.287 20.8984 46.778 15.1107C45.9688 1.21411 25.1515 -3.93281 14.2647 3.19932Q3.7454 10.0908 7.16766 23.641C7.31281 24.2158 7.10745 24.8404 6.68837 25.2596Q4.65477 27.2939 1.90678 32.0955Z" fill="currentColor"/>
  </svg>
);

const CheckIcon: React.FC<{ className?: string }> = ({ className = "w-5 h-5" }) => (
  <svg className={className} viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" fill="currentColor"/>
  </svg>
);

const ButtonIcon: React.FC<{ className?: string }> = ({ className = "w-4 h-4" }) => (
  <svg className={className} viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 8a5 5 0 1110 0A5 5 0 013 8zm5-3a3 3 0 100 6 3 3 0 000-6z" fill="currentColor"/>
  </svg>
);

const DecorativeIcon: React.FC<{ className?: string }> = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L2 7v10c0 5.55 3.84 9.74 9 11 5.16-1.26 9-5.45 9-11V7l-10-5z" fill="currentColor"/>
  </svg>
);

// 图标组件映射
const IconComponent: React.FC<{ icon: string; className?: string }> = ({ icon, className }) => {
  switch (icon) {
    case 'logo':
      return <LogoIcon className={className} />;
    case 'check':
      return <CheckIcon className={className} />;
    case 'button':
      return <ButtonIcon className={className} />;
    case 'decorative':
      return <DecorativeIcon className={className} />;
    default:
      return <div className={`${className} bg-gray-200 rounded`} />;
  }
};

const defaultCoreFeatures: CoreFeature[] = [
  {
    id: 'resume-diagnosis',
    title: 'Resume Diagnosis',
    description: 'Deep optimization: Evaluate matching through 20+ dimensions (ATS compatibility, keyword density, achievement quantification)',
    icon: 'resume',
  },
  {
    id: 'interview-simulation',
    title: 'Multi-Scenario Interview Simulation',
    description: 'Dynamic rewriting suggestions: Highlight problematic sentences in real time and provide customized industry-specific scripts (such as optimization of quantitative indicators for technical positions)',
    icon: 'interview',
  },
  {
    id: 'real-time-assistance',
    title: 'Real-Time Interview Assistance',
    description: 'Job Search Success Rate Increased by 3 Times',
    icon: 'assistance',
  },
];

const defaultWhyChooseStats: Statistic[] = [
  {
    id: 'success-rate',
    value: '89%',
    description: 'Interview Success Rate – Surpassing industry benchmarks by 35%',
  },
  {
    id: 'satisfaction',
    value: '95%',
    description: 'User Satisfaction – Redefining career coaching standards',
  },
  {
    id: 'mock-interviews',
    value: '1.2M+',
    description: 'Mock Interviews Conducted – Equivalent to 150 years of human training',
  },
  {
    id: 'resumes',
    value: '380,000',
    description: 'Resumes Professionally Optimized – Aligned with Fortune 500 hiring criteria',
  },
];

const defaultTestimonials: Testimonial[] = [
  {
    id: 'pm-testimonial',
    name: 'Sarah Chen',
    role: 'Product Manager',
    content: 'This platform\'s resume analysis helped me strategically highlight 0-to-1 product launches. The AI interviewer drilled me on balancing UX vs. monetization tradeoffs – exactly the curveball questions PM interviews throw at you! The mock PRD walkthroughs and stakeholder alignment scenarios are gold.',
    avatar: 'avatar-pm.svg',
  },
  {
    id: 'marketing-testimonial',
    name: 'Michael Rodriguez',
    role: 'Marketing Manager',
    content: '10 years in marketing, yet the resume audit exposed my blind spot: listing campaign metrics without proving ROI attribution or budget optimization skills. The crisis simulation? Brilliant! Finally transitioned from "campaign executor" to "growth strategist" – worth every penny!',
    avatar: 'avatar-marketing.svg',
  },
  {
    id: 'data-testimonial',
    name: 'Alex Johnson',
    role: 'Data Analyst',
    content: 'Stop stuffing your resume with "built Python models"! This platform taught me to showcase business impact: "Reduced CAC by 23% via churn-prediction models" > vague tech jargon. Mock interviews crushed me (in the best way) – from defending A/B testing significance levels to explaining neural nets to CMOs.',
    avatar: 'avatar-data.svg',
  },
];

const defaultFAQItems: FAQItem[] = [
  {
    id: 'positions-industries',
    question: 'What specific positions and industries is OfferOtter suitable for?',
    answer: 'OfferOtter is a comprehensive career development platform designed specifically for recent graduates. We understand the challenges you may face when entering the workforce, so we offer a range of professional support to help you transition smoothly into your career. Whether you are a software engineer or a newcomer in any other field, OfferOtter provides professional interview guidance and industry knowledge training.',
    isExpanded: false,
  },
  {
    id: 'data-security',
    question: 'Is my interview data secure?',
    answer: 'Yes, we take data security very seriously. All interview data is encrypted and stored securely. We comply with industry-standard security protocols and never share your personal information with third parties.',
    isExpanded: false,
  },
  {
    id: 'weekend-preparation',
    question: 'I only have weekends to prepare for the interview, how can OfferOtter help me complete it quickly?',
    answer: 'Our platform is designed for efficient learning. You can complete a comprehensive interview preparation in just a few weekend sessions with our focused modules and AI-powered practice sessions.',
    isExpanded: false,
  },
  {
    id: 'detection',
    question: 'Will you be detected using OfferOtter?',
    answer: 'No, OfferOtter is designed as a training platform. The skills and knowledge you gain are yours, and there\'s no way for employers to detect that you\'ve used our platform during your preparation.',
    isExpanded: false,
  },
  {
    id: 'complex-questions',
    question: 'Can OfferOtter truly understand and answer complex interview questions?',
    answer: 'Yes, our AI is trained on thousands of real interview scenarios across various industries. It can handle complex behavioral, technical, and situational questions with contextually appropriate responses.',
    isExpanded: false,
  },
];

export const OfferotterHome: React.FC<OfferotterHomeProps> = ({
  className,
  theme = 'light',
  heroTitle = 'OfferOtter Master Your Dream Job Interview',
  heroSubtitle,
  statistics = {
    resumesAnalyzed: '380,000+',
    interviewParticipants: '1,200,000',
  },
  coreFeatures = defaultCoreFeatures,
  whyChooseStats = defaultWhyChooseStats,
  testimonials = defaultTestimonials,
  faqItems = defaultFAQItems,
  onGetStarted,
  onWatchDemo,
  onContactUs,
  onLogin,
}) => {
  const [expandedFAQ, setExpandedFAQ] = useState<string | null>(null);

  const toggleFAQ = (id: string) => {
    setExpandedFAQ(expandedFAQ === id ? null : id);
  };

  const handleGetStarted = () => {
    onGetStarted?.();
  };

  const handleWatchDemo = () => {
    onWatchDemo?.();
  };

  const handleContactUs = () => {
    onContactUs?.();
  };

  const handleLogin = () => {
    onLogin?.();
  };

  return (
    <main 
      className={`min-h-screen bg-white ${theme === 'dark' ? 'dark' : ''} ${className || ''}`}
      role="main"
    >
      {/* Navigation Header */}
      <header className="relative bg-white backdrop-blur-md bg-opacity-60 shadow-sm">
        <nav className="container mx-auto px-6 py-4 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <IconComponent icon="logo" className="text-amber-700" />
            <span className="font-bold text-xl text-amber-700" style={{ fontFamily: 'Pump Demi Bold LET' }}>
              Offerotter
            </span>
          </div>

          {/* Navigation Menu */}
          <div className="hidden md:flex items-center space-x-8">
            <a href="#" className="text-blue-600 font-bold text-lg">Home</a>
            <a href="#" className="text-gray-700 hover:text-blue-600 text-lg">Pricing</a>
            <button 
              onClick={handleContactUs}
              className="text-gray-700 hover:text-blue-600 text-lg"
            >
              Contact Us
            </button>
            <button
              onClick={handleLogin}
              className="bg-blue-100 hover:bg-blue-200 px-6 py-2 rounded-full text-blue-700 font-medium transition-colors duration-200 flex items-center space-x-2"
              aria-label="Login"
            >
              <span>Login</span>
            </button>
            <button
              onClick={handleGetStarted}
              className="bg-gray-100 hover:bg-gray-200 px-6 py-2 rounded-full text-gray-700 font-medium transition-colors duration-200 flex items-center space-x-2"
              aria-label="Get started for free"
            >
              <span>Get Start for Free</span>
            </button>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        {/* Background gradients */}
        <div className="absolute inset-0 bg-gradient-to-b from-blue-50 to-blue-100 opacity-60"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-blue-200 rounded-full opacity-20 blur-3xl"></div>
        
        <div className="container mx-auto px-6 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-medium text-gray-800 mb-8 leading-tight" style={{ fontFamily: 'Poppins' }}>
              {heroTitle}
            </h1>
            
            {heroSubtitle && (
              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                {heroSubtitle}
              </p>
            )}
            
            {/* Statistics Badge */}
            <div className="inline-block bg-white bg-opacity-20 backdrop-blur-sm rounded-full px-8 py-4 mb-12 shadow-sm">
              <p className="text-blue-600 font-semibold">
                {statistics.resumesAnalyzed} resumes have been analyzed, and the number of participants in simulated interviews has exceeded {statistics.interviewParticipants}
              </p>
            </div>

            {/* Key Features */}
            <div className="flex flex-col md:flex-row justify-center items-center space-y-4 md:space-y-0 md:space-x-8 mb-16">
              {coreFeatures.slice(0, 3).map((feature) => (
                <div key={feature.id} className="flex items-center space-x-3 bg-white bg-opacity-30 backdrop-blur-sm rounded-lg px-4 py-3 shadow-sm">
                  <div className="w-8 h-8 bg-black rounded-full flex items-center justify-center">
                    <IconComponent icon="check" className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-gray-700 font-medium">{feature.title}</span>
                </div>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
              <button
                onClick={handleGetStarted}
                className="bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white px-8 py-4 rounded-full font-medium text-lg transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
                aria-label="Get started for free"
              >
                <span>Get Start for Free</span>
                <IconComponent icon="button" className="w-5 h-5" />
              </button>
              <button
                onClick={handleWatchDemo}
                className="bg-white bg-opacity-80 hover:bg-opacity-100 text-gray-700 px-8 py-4 rounded-full font-medium text-lg transition-all duration-200 shadow-md hover:shadow-lg"
                aria-label="Watch the demo"
              >
                Watch The Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Core Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-medium text-gray-800 mb-4" style={{ fontFamily: 'Poppins' }}>
              Core Features
            </h2>
            <IconComponent icon="decorative" className="w-6 h-6 mx-auto text-blue-600" />
          </div>

          <div className="bg-blue-50 rounded-3xl p-8 md:p-16 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-50 to-blue-100 opacity-50"></div>
            
            <div className="relative z-10 grid md:grid-cols-3 gap-8">
              {coreFeatures.map((feature) => (
                <div key={feature.id} className="text-center md:text-left">
                  <div className="inline-block p-4 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl mb-6">
                    <IconComponent icon="check" className="w-8 h-8 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose OfferOtter Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-medium text-gray-800 mb-4" style={{ fontFamily: 'Poppins' }}>
              Why Choose OfferOtter
            </h2>
            <IconComponent icon="decorative" className="w-6 h-6 mx-auto text-blue-600" />
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {whyChooseStats.map((stat) => (
              <div key={stat.id} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-5xl font-bold text-blue-800">{stat.value}</span>
                  <IconComponent icon="decorative" className="w-16 h-16 text-blue-200" />
                </div>
                <p className="text-blue-800 font-semibold text-sm leading-relaxed">{stat.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* User Testimonials Section */}
      <section className="py-20 bg-blue-50">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-medium text-gray-800 mb-4" style={{ fontFamily: 'Poppins' }}>
              Real Stories from Users
            </h2>
            <IconComponent icon="decorative" className="w-6 h-6 mx-auto text-blue-600" />
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="bg-white rounded-2xl p-6 shadow-lg backdrop-blur-md bg-opacity-90">
                <div className="w-16 h-16 mx-auto mb-4 overflow-hidden rounded-full">
                  <img 
                    src={`/images/${testimonial.avatar}`} 
                    alt={`${testimonial.name} avatar`}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const nextEl = e.currentTarget.nextElementSibling as HTMLElement;
                      if (nextEl) nextEl.style.display = 'block';
                    }}
                  />
                  <div className="w-16 h-16 bg-gray-300 rounded-full flex items-center justify-center hidden">
                    <span className="text-gray-600 text-xs font-semibold">{testimonial.role.split(' ').map(w => w[0]).join('')}</span>
                  </div>
                </div>
                <h4 className="text-xl font-semibold text-gray-800 text-center mb-2">{testimonial.role}</h4>
                <p className="text-gray-600 text-sm leading-relaxed text-center mb-4">"{testimonial.content}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-medium text-gray-800 mb-4" style={{ fontFamily: 'Poppins' }}>
              Any Questions?
            </h2>
            <p className="text-xl text-blue-600 font-medium">And we have got answers to all of them</p>
          </div>

          <div className="max-w-4xl mx-auto space-y-4">
            {faqItems.map((item) => (
              <div key={item.id} className="bg-blue-50 rounded-3xl overflow-hidden">
                <button
                  onClick={() => toggleFAQ(item.id)}
                  className="w-full text-left p-6 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-expanded={expandedFAQ === item.id}
                >
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-semibold text-gray-800">{item.question}</h3>
                    <div className={`transform transition-transform duration-200 ${expandedFAQ === item.id ? 'rotate-180' : ''}`}>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </div>
                  </div>
                </button>
                {expandedFAQ === item.id && (
                  <div className="px-6 pb-6">
                    <p className="text-gray-600 leading-relaxed">{item.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-blue-50 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-100 to-blue-200 opacity-60"></div>
        <div className="container mx-auto px-6 relative z-10 text-center">
          <h2 className="text-3xl font-medium text-gray-800 mb-8" style={{ fontFamily: 'Poppins' }}>
            OfferOtter Master Your Dream Job Interview with AI-Powered Simulation
          </h2>
          <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
            <button
              onClick={handleGetStarted}
              className="bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white px-8 py-4 rounded-full font-medium text-lg transition-all duration-200 shadow-lg hover:shadow-xl flex items-center space-x-2"
              aria-label="Get started for free"
            >
              <span>Get Start for Free</span>
              <IconComponent icon="button" className="w-5 h-5" />
            </button>
            <button
              onClick={handleWatchDemo}
              className="bg-white bg-opacity-80 hover:bg-opacity-100 text-gray-700 px-8 py-4 rounded-full font-medium text-lg transition-all duration-200 shadow-md hover:shadow-lg"
              aria-label="Watch the demo"
            >
              Watch The Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-blue-50 py-12">
        <div className="container mx-auto px-6">
          <div className="text-center space-y-4">
            <IconComponent icon="decorative" className="w-6 h-6 mx-auto opacity-50 text-gray-400" />
            <div className="flex justify-center space-x-8">
              <a href="#" className="text-gray-600 hover:text-gray-800 font-light">Privacy Policy</a>
              <a href="#" className="text-gray-600 hover:text-gray-800 font-light">Terms of Use</a>
            </div>
            <p className="text-gray-600 font-light">
              Copyright: © 2025 OfferOtter, Inc. All Rights Reserved.
            </p>
          </div>
        </div>
      </footer>
    </main>
  );
}; 