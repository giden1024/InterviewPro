import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { OfferotterHome } from '../OfferotterHome';
import type { OfferotterHomeProps } from '../types';

describe('OfferotterHome Component', () => {
  const defaultProps: OfferotterHomeProps = {
    onGetStarted: jest.fn(),
    onWatchDemo: jest.fn(),
    onContactUs: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    it('renders the component without crashing', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByRole('main')).toBeInTheDocument();
    });

    it('renders with custom className', () => {
      render(<OfferotterHome {...defaultProps} className="custom-class" />);
      expect(screen.getByRole('main')).toHaveClass('custom-class');
    });

    it('renders hero title correctly', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText(/OfferOtter Master Your Dream Job Interview/i)).toBeInTheDocument();
    });

    it('renders custom hero title when provided', () => {
      const customTitle = 'Custom Interview Platform';
      render(<OfferotterHome {...defaultProps} heroTitle={customTitle} />);
      expect(screen.getByText(customTitle)).toBeInTheDocument();
    });
  });

  describe('Navigation Section', () => {
    it('renders navigation menu items', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Pricing')).toBeInTheDocument();
      expect(screen.getByText('Contact Us')).toBeInTheDocument();
    });

    it('renders logo with brand name', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Offerotter')).toBeInTheDocument();
    });

    it('calls onContactUs when Contact Us is clicked', () => {
      render(<OfferotterHome {...defaultProps} />);
      fireEvent.click(screen.getByText('Contact Us'));
      expect(defaultProps.onContactUs).toHaveBeenCalledTimes(1);
    });
  });

  describe('Hero Section', () => {
    it('renders statistics display', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText(/380,000\+ resumes have been analyzed/i)).toBeInTheDocument();
      expect(screen.getByText(/1,200,000/i)).toBeInTheDocument();
    });

    it('renders custom statistics when provided', () => {
      const customStats = {
        resumesAnalyzed: '500,000+',
        interviewParticipants: '2,000,000',
      };
      render(<OfferotterHome {...defaultProps} statistics={customStats} />);
      expect(screen.getByText(/500,000\+/)).toBeInTheDocument();
      expect(screen.getByText(/2,000,000/)).toBeInTheDocument();
    });

    it('renders core feature highlights', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Resume Diagnosis')).toBeInTheDocument();
      expect(screen.getByText('Multi-Scenario Interview Simulation')).toBeInTheDocument();
      expect(screen.getByText(/Real-Time Interview Plug-in Assistance/i)).toBeInTheDocument();
    });
  });

  describe('Core Features Section', () => {
    it('renders section title', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Core Features')).toBeInTheDocument();
    });

    it('renders default feature cards', () => {
      render(<OfferotterHome {...defaultProps} />);
      // Check for feature descriptions
      expect(screen.getByText(/Deep optimization/i)).toBeInTheDocument();
      expect(screen.getByText(/Dynamic rewriting suggestions/i)).toBeInTheDocument();
    });

    it('renders custom core features when provided', () => {
      const customFeatures = [
        {
          id: 'feature1',
          title: 'Custom Feature 1',
          description: 'Custom description 1',
          icon: 'icon1',
        },
        {
          id: 'feature2',
          title: 'Custom Feature 2',
          description: 'Custom description 2',
          icon: 'icon2',
        },
      ];
      render(<OfferotterHome {...defaultProps} coreFeatures={customFeatures} />);
      expect(screen.getByText('Custom Feature 1')).toBeInTheDocument();
      expect(screen.getByText('Custom Feature 2')).toBeInTheDocument();
    });
  });

  describe('Why Choose Section', () => {
    it('renders section title', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Why Choose OfferOtter')).toBeInTheDocument();
    });

    it('renders key statistics', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('89%')).toBeInTheDocument();
      expect(screen.getByText('95%')).toBeInTheDocument();
      expect(screen.getByText('1.2M+')).toBeInTheDocument();
      expect(screen.getByText('380,000')).toBeInTheDocument();
    });

    it('renders statistics descriptions', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText(/Interview Success Rate/i)).toBeInTheDocument();
      expect(screen.getByText(/User Satisfaction/i)).toBeInTheDocument();
      expect(screen.getByText(/Mock Interviews Conducted/i)).toBeInTheDocument();
      expect(screen.getByText(/Resumes Professionally Optimized/i)).toBeInTheDocument();
    });
  });

  describe('Testimonials Section', () => {
    it('renders section title', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Real Stories from Users')).toBeInTheDocument();
    });

    it('renders default testimonials', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Product Manager')).toBeInTheDocument();
      expect(screen.getByText('Marketing Manager')).toBeInTheDocument();
      expect(screen.getByText('Data Analyst')).toBeInTheDocument();
    });

    it('renders testimonial content', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText(/resume analysis helped me strategically/i)).toBeInTheDocument();
      expect(screen.getByText(/10 years in marketing/i)).toBeInTheDocument();
    });

    it('renders custom testimonials when provided', () => {
      const customTestimonials = [
        {
          id: 'test1',
          name: 'John Doe',
          role: 'Software Engineer',
          content: 'Great platform!',
          avatar: 'avatar1.svg',
        },
      ];
      render(<OfferotterHome {...defaultProps} testimonials={customTestimonials} />);
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Great platform!')).toBeInTheDocument();
    });
  });

  describe('FAQ Section', () => {
    it('renders section title', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Any Questions?')).toBeInTheDocument();
      expect(screen.getByText(/we have got answers to all of them/i)).toBeInTheDocument();
    });

    it('renders default FAQ items', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText(/What specific positions and industries/i)).toBeInTheDocument();
      expect(screen.getByText(/Is my interview data secure/i)).toBeInTheDocument();
    });

    it('toggles FAQ item expansion on click', async () => {
      render(<OfferotterHome {...defaultProps} />);
      const faqButton = screen.getByText(/What specific positions and industries/i);
      
      fireEvent.click(faqButton);
      await waitFor(() => {
        expect(screen.getByText(/OfferOtter is a comprehensive career development platform/i)).toBeVisible();
      });
    });
  });

  describe('CTA Section', () => {
    it('renders CTA buttons', () => {
      render(<OfferotterHome {...defaultProps} />);
      const getStartedButtons = screen.getAllByText(/Get Start for Free/i);
      const watchDemoButton = screen.getByText(/Watch The Demo/i);
      
      expect(getStartedButtons.length).toBeGreaterThan(0);
      expect(watchDemoButton).toBeInTheDocument();
    });

    it('calls onGetStarted when Get Started button is clicked', () => {
      render(<OfferotterHome {...defaultProps} />);
      const getStartedButton = screen.getAllByText(/Get Start for Free/i)[0];
      fireEvent.click(getStartedButton);
      expect(defaultProps.onGetStarted).toHaveBeenCalledTimes(1);
    });

    it('calls onWatchDemo when Watch Demo button is clicked', () => {
      render(<OfferotterHome {...defaultProps} />);
      const watchDemoButton = screen.getByText(/Watch The Demo/i);
      fireEvent.click(watchDemoButton);
      expect(defaultProps.onWatchDemo).toHaveBeenCalledTimes(1);
    });
  });

  describe('Footer Section', () => {
    it('renders footer links', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
      expect(screen.getByText('Terms of Use')).toBeInTheDocument();
    });

    it('renders copyright notice', () => {
      render(<OfferotterHome {...defaultProps} />);
      expect(screen.getByText(/© 2025 OfferOtter, Inc. All Rights Reserved/i)).toBeInTheDocument();
    });
  });

  describe('Interactive States', () => {
    it('handles hover states on buttons', () => {
      render(<OfferotterHome {...defaultProps} />);
      const button = screen.getAllByText(/Get Start for Free/i)[0];
      
      fireEvent.mouseEnter(button);
      expect(button).toHaveClass('hover:shadow-lg');
    });

    it('handles focus states for accessibility', () => {
      render(<OfferotterHome {...defaultProps} />);
      const button = screen.getAllByText(/Get Start for Free/i)[0];
      
      fireEvent.focus(button);
      expect(button).toHaveClass('focus:ring-2');
    });
  });

  describe('Responsive Behavior', () => {
    it('adapts layout for mobile screens', () => {
      // Mock window.innerWidth
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 600,
      });

      render(<OfferotterHome {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('container');
    });

    it('shows desktop layout for larger screens', () => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      });

      render(<OfferotterHome {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('container');
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels on interactive elements', () => {
      render(<OfferotterHome {...defaultProps} />);
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAttribute('aria-label');
      });
    });

    it('supports keyboard navigation', () => {
      render(<OfferotterHome {...defaultProps} />);
      const button = screen.getAllByText(/Get Start for Free/i)[0];
      
      fireEvent.keyDown(button, { key: 'Enter', code: 'Enter' });
      expect(defaultProps.onGetStarted).toHaveBeenCalled();
    });

    it('has proper heading hierarchy', () => {
      render(<OfferotterHome {...defaultProps} />);
      const headings = screen.getAllByRole('heading');
      expect(headings.length).toBeGreaterThan(0);
    });
  });

  describe('Theme Support', () => {
    it('applies light theme by default', () => {
      render(<OfferotterHome {...defaultProps} />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('bg-white');
    });

    it('applies dark theme when specified', () => {
      render(<OfferotterHome {...defaultProps} theme="dark" />);
      const main = screen.getByRole('main');
      expect(main).toHaveClass('dark');
    });
  });
}); 