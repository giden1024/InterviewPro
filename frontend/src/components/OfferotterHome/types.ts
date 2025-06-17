export interface CoreFeature {
  id: string;
  title: string;
  description: string;
  icon: string;
}

export interface Statistic {
  id: string;
  value: string;
  description: string;
  icon?: string;
}

export interface Testimonial {
  id: string;
  name: string;
  role: string;
  content: string;
  avatar: string;
}

export interface FAQItem {
  id: string;
  question: string;
  answer: string;
  isExpanded?: boolean;
}

export interface OfferotterHomeProps {
  // Theme and styling
  className?: string;
  theme?: 'light' | 'dark';
  
  // Content customization
  heroTitle?: string;
  heroSubtitle?: string;
  statistics?: {
    resumesAnalyzed: string;
    interviewParticipants: string;
  };
  
  // Feature sections
  coreFeatures?: CoreFeature[];
  whyChooseStats?: Statistic[];
  testimonials?: Testimonial[];
  faqItems?: FAQItem[];
  
  // Interactive callbacks
  onGetStarted?: () => void;
  onWatchDemo?: () => void;
  onContactUs?: () => void;
  onLogin?: () => void;
} 