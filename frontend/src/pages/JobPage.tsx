import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobService, Job, JobTemplate, CreateJobData } from '../services/jobService';

const JobPage: React.FC = () => {
  const navigate = useNavigate();
  
  // State management
  const [selectedJobType, setSelectedJobType] = useState<string>('');
  const [jobTitle, setJobTitle] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [jobUrl, setJobUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [dragActive, setDragActive] = useState(false);

  // Preset job types
  const jobTypes = [
    'Product Manager',
    'Customer Service',
    'Marketing',
    'Accountant',
    'Sales Specialist',
    'Data Engineer',
    'User Operations',
    'Operations Manager'
  ];

  // Job data from docs/job desction.md
  const jobData = {
    'Product Manager': {
      title: 'Product Manager',
      description: `Job Responsibilities
1. Independently responsible for the full-link product design, function design, and strategy optimization of a vertical industry user for a recruitment app.
2. Deeply explore the needs of vertical industry users, analyze user behavior, and cooperate with industry research teams to define the real needs and problems of users in job recruitment.
3. Solve user needs and problems through various product methods, including but not limited to product path design, function design, and strategy iteration optimization, and be responsible for improving vertical user behavior data indicators.
4. Curiosity-driven, able to proactively explore different types of users and industries in job recruitment scenarios and design product solutions that are compatible with existing product forms and meet more personalized needs.

Job Requirements
1. Bachelor's degree or above, with more than one year of product work experience, experience with user-end products, social networking, and e-commerce preferred, having user growth and representative product features is a plus.
2. A certain pursuit of product aesthetics, experience in product experience optimization (1-N) preferred.
3. Divergent thinking and good summarization skills; excellent data thinking and good data review habits.
4. Strong self-drive, good at communication and collaboration, strong sense of responsibility, and team spirit.`
    },
    'Customer Service': {
      title: 'Customer Service',
      description: `Job Responsibilities
1. Independently responsible for potential high-risk user feedback and public opinion information from various channels, promptly identify and warn, collaborate with all parties to formulate and follow up solutions.
2. Quickly make objective judgments on high-risk feedback and handle it flexibly and professionally to avoid risks while ensuring user satisfaction.
3. Provide knowledge and skill support to customer service specialists based on team business needs, help frontline customer service handle difficult issues, and cooperate with service operations to feedback business gaps.
4. Deeply understand business and products, and solve user feedback in a timely and professional manner from various dimensions.
5. Good at summarizing and assisting the team in formulating mechanisms for identifying and handling high-risk user feedback.

Job Requirements
1. Bachelor's degree or above, with experience in user service and customer service operations, local life industry experience is a plus.
2. Flexible thinking, quick learning ability, good communication and negotiation skills, experience in handling public opinion and customer communication.
3. User-centric, strong sense of service, responsible, reliable, and practical.
4. Quickly locate problem causes, formulate flexible solutions, and ensure a good user service experience.`
    },
    'Marketing': {
      title: 'Marketing Planner',
      description: `Job Responsibilities
1. Insight into target user needs, formulate overall brand positioning and medium- to long-term brand communication plans.
2. Formulate effective annual promotion plans, lead planning and implementation of major marketing projects, enhance brand awareness, reputation, and user preference.
3. Based on brand goals, flexibly use various resources, and integrate public relations, new media, ground promotion, and other resources to create creative communication solutions.
4. Integrate high-quality resources and coordinate internal and external teams to complete various project plans, ensure the smooth implementation of major marketing projects and communication effects.

Job Requirements
1. Bachelor's degree or above, with more than five years of work experience in marketing planning and brand promotion, rich experience in new media marketing, with successful planning cases preferred.
2. Strong logical thinking, good at proposing effective marketing solutions based on market insights.
3. Sensitive to marketing information, strong ability to integrate and plan resources, and strong project execution ability.
4. Good communication, coordination, and expression skills, strong pressure resistance and sense of responsibility.`
    },
    'Accountant': {
      title: 'Accountant',
      description: `Job Responsibilities
1. Collect various sales data and prepare related statistical reports.
2. Responsible for preparing accounting vouchers, accounting, and financial statements.
3. Responsible for accounting, financial budgeting, analysis, and supervision.
4. Responsible for handling accounts receivable and payable with the company's business.
5. Responsible for recording and auditing various expenses, preparing vouchers, and accounting.
6. Regularly submit various financial reports as required by the company.
7. Daily company affairs and other related work assigned by the leader.
8. Monthly interface with external accountants for financial reports.

Job Requirements
1. College degree or above, graduated from a finance-related major, with accounting-related certificates.
2. Master basic financial professional knowledge and proficiently operate Excel, Word, and other office software.
3. Maintain good professional ethics, keep confidential important company information, reports, and documents.
4. Able to complete financial reports independently.
5. No age limit, retirees are also welcome.`
    },
    'Sales Specialist': {
      title: 'Sales Specialist',
      description: `Job Responsibilities
1. Communicate effectively with customers via phone based on company-provided effective data to understand customer needs and provide professional course sales services.
2. Complete sales and payment work based on the company's product marketing strategy.
3. Maintain good long-term cooperative relationships with existing customers through regular communication.
4. Collect and summarize potential customer trends and timely understand market information.
5. Actively complete other tasks assigned by the leader. Working hours: Monday to Friday 8:00-17:30, weekends off, national holidays off (paid annual leave, extended Chinese New Year holiday).

Job Requirements
1. Aged 18-35, high school diploma or above, excellent candidates can be considered for relaxation.
2. Accept fresh graduates with paid training.
3. Passionate about sales work, cheerful, resilient, quick-thinking, good adaptability, excellent verbal expression skills, team spirit, and challenges high salaries.
4. Preferably with related work experience in online sales, sales, telemarketing, or customer service.`
    },
    'Data Engineer': {
      title: 'Data Engineer',
      description: `Job Responsibilities
1. Design, develop, and maintain scalable data pipelines and ETL processes.
2. Build and optimize data models for efficient data storage and retrieval.
3. Implement data quality checks and monitoring systems to ensure data accuracy and integrity.
4. Collaborate with data scientists and analysts to understand data requirements and provide efficient data solutions.
5. Develop and maintain data warehouses and data lakes to support business intelligence and analytics.
6. Implement and manage big data technologies to process and analyze large volumes of data.
7. Optimize data systems for performance, scalability, and reliability.
8. Stay up-to-date with emerging technologies and industry trends in data engineering.

Job Requirements
1. Bachelor's degree in Computer Science, Software Engineering, or related field.
2. 3+ years of experience in data engineering or similar roles.
3. Strong programming skills in languages such as Python, Java, or Scala.
4. Proficiency in SQL and experience with relational databases (e.g., MySQL, PostgreSQL) and NoSQL databases (e.g., MongoDB, Cassandra).
5. Experience with big data technologies such as Hadoop, Spark, and Hive.
6. Knowledge of data warehousing concepts and experience with tools like Snowflake, Redshift, or BigQuery.
7. Familiarity with cloud platforms (AWS, GCP, or Azure) and their data services.
8. Experience with data visualization tools (e.g., Tableau, Power BI) is a plus.
9. Strong problem-solving skills and ability to work in a fast-paced, collaborative environment.`
    },
    'User Operations': {
      title: 'User Operations Specialist/Manager',
      description: `Job Responsibilities
1. Drive user acquisition, activation, and retention strategies through localized campaigns (e.g., social media, SEO/SEM) in target markets such as Bangladesh/Pakistan, North America, or Germany.
2. Analyze user behavior data (e.g., CTR, CAC, CLV) to refine growth tactics and improve retention rates.
3. Build and manage online user communities (e.g., Facebook Groups, forums), resolve user issues promptly, and maintain relationships with VIP users/KOLs.
4. Collect and analyze user feedback to inform product improvements and optimize user experience.
5. Partner with product, engineering, and marketing teams to enhance onboarding processes and reduce churn.
6. Develop localized content strategies and organize events to boost engagement (e.g., live streams, regional campaigns).
7. Track KPIs (e.g., DAU, MRR, activation rates) and generate actionable insights for strategy adjustments.
8. Conduct user research and A/B testing to validate operational initiatives.

Job Requirements
1. Bachelor's degree in Marketing, Business, Communications, or related fields.
2. 1-3+ years in user operations, community management, or digital marketing, preferably in tech, social media, or entertainment industries.
3. Soft Skills: Strong communication, empathy, and cultural adaptability for global user engagement.
4. Attributes: Proactive, detail-oriented, and passionate about mobile apps/social media trends.`
    },
    'Operations Manager': {
      title: 'Operations Manager',
      description: `Job Responsibilities
1. Develop, implement, and optimize daily operational processes to improve efficiency and reduce costs.
2. Establish and monitor KPIs (e.g., productivity, budget adherence) to ensure alignment with organizational goals.
3. Lead cross-departmental collaboration to streamline workflows and resolve bottlenecks.
4. Recruit, train, and manage staff, fostering a high-performance culture through mentorship and performance evaluations.
5. Oversee employee safety, compliance with regulations (e.g., OSHA), and workplace standards.
6. Manage operational budgets, financial forecasting, and cost-saving initiatives.
7. Oversee inventory control, vendor negotiations, and procurement to ensure cost-effective resource allocation.

Job Requirements
1. Education: Bachelor's degree in Business Administration, Operations Management, or a related field. Master's degree preferred.
2. 3-5+ years in operations management, preferably in industries like manufacturing, tech, or construction.
3. Technical: Proficiency in ERP systems, data analysis tools, and Microsoft Office.
4. Leadership: Strong decision-making, conflict resolution, and mentorship abilities.
5. Communication: Excellent verbal/written communication for cross-functional and stakeholder engagement.
6. Certifications (optional): Lean Six Sigma, PMP, or industry-specific credentials (e.g., EMT certification for healthcare roles).
7. Attributes: Strategic thinker, adaptable to fast-paced environments, and detail-oriented.`
    }
  };

  // Handle file drag
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileUpload = async (file: File) => {
    // 检查文件类型
    const imageExtensions = ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'webp'];
    const fileExtension = file.name.split('.').pop()?.toLowerCase();
    
    if (imageExtensions.includes(fileExtension || '')) {
      // 处理图片文件 - OCR识别
      setLoading(true);
      setError('');
      
      try {
        console.log('开始OCR文字识别:', file.name);
        const result = await jobService.extractTextFromImage(file);
        
        if (result.text) {
          // 将识别的文本填充到Job description文本框
          setJobDescription(result.text);
          console.log('OCR识别成功，文本已填充到Job description');
        } else {
          setError('Unable to recognize text from the image');
        }
      } catch (err: any) {
        console.error('OCR识别失败:', err);
        setError(err.message || 'Image text recognition failed, please try again');
      } finally {
        setLoading(false);
      }
    } else {
      // 其他文件类型的处理逻辑
      console.log('File uploaded:', file);
      setError('Please upload an image file (supported formats: PNG, JPG, JPEG, BMP, TIFF, WEBP)');
    }
  };

  // Handle job type selection
  const handleJobTypeSelect = (jobType: string) => {
    setSelectedJobType(jobType);
    
    // Auto-fill job title and description from predefined data
    if (jobData[jobType as keyof typeof jobData]) {
      const selectedJobData = jobData[jobType as keyof typeof jobData];
      setJobTitle(selectedJobData.title);
      setJobDescription(selectedJobData.description);
      console.log(`Selected job type: ${jobType}, auto-filled title and description`);
    } else {
      // Fallback to just setting the job type as title
      setJobTitle(jobType);
    }
    
    setError(''); // Clear error message
  };

  // Handle job title input
  const handleJobTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setJobTitle(e.target.value);
    if (error) setError(''); // Clear error message
  };

  // Handle job description input
  const handleJobDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setJobDescription(e.target.value);
    if (error) setError(''); // Clear error message
  };

  // Handle next step
  const handleNext = () => {
    if (!jobTitle.trim()) {
      setError('Please enter job title');
      return;
    }

    if (!jobDescription.trim()) {
      setError('Please enter job description');
      return;
    }

    navigate('/resume', {
      state: {
        jobTitle: jobTitle,
        jobDescription: jobDescription,
        selectedJobType: selectedJobType
      }
    });
  };

  // Handle return to home
  const handleHome = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#EEF9FF' }}>
      <div className="container mx-auto px-6 py-12 max-w-7xl">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="bg-white rounded-full px-8 py-4 shadow-lg flex items-center space-x-16">
            {/* Job Step - Active */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderColor: '#282828'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                  <path d="M8 2L6 4h4l-2-2zM4 6v8h8V6H4z"/>
                </svg>
              </div>
              <span 
                className="text-lg font-semibold"
                style={{ 
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '600',
                  color: '#006FA2'
                }}
              >
                Job
              </span>
            </div>

            {/* Arrow */}
            <div 
              className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                borderColor: '#282828'
              }}
            >
              <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                <path d="M6 4l4 4-4 4V4z"/>
              </svg>
            </div>

            {/* Resume Step */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderColor: '#282828'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                  <path d="M6 4l4 4-4 4V4z"/>
                </svg>
              </div>
              <span 
                className="text-lg"
                style={{ 
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '400',
                  color: '#282828'
                }}
              >
                Resume
              </span>
            </div>

            {/* Arrow */}
            <div 
              className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
              style={{ 
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                borderColor: '#282828'
              }}
            >
              <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                <path d="M6 4l4 4-4 4V4z"/>
              </svg>
            </div>

            {/* Complete Step */}
            <div className="flex items-center space-x-4">
              <div 
                className="w-9 h-9 rounded-full border-2 border-dashed flex items-center justify-center"
                style={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  borderColor: '#282828'
                }}
              >
                <svg className="w-4 h-4" style={{ color: '#282828' }} fill="currentColor" viewBox="0 0 16 16">
                  <path d="M6 4l4 4-4 4V4z"/>
                </svg>
              </div>
              <span 
                className="text-lg"
                style={{ 
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '400',
                  color: '#282828'
                }}
              >
                Complete
              </span>
            </div>
          </div>
        </div>

        {/* Main Title */}
        <div className="text-center mb-8">
          <h1 
            className="mb-4"
            style={{
              fontFamily: 'Poppins',
              fontSize: '23px',
              fontWeight: '500',
              lineHeight: '127.07%',
              color: '#262626'
            }}
          >
            Which job interview are you preparing for?
          </h1>
          <p 
            style={{
              fontFamily: 'Poppins',
              fontSize: '15px',
              fontWeight: '400',
              lineHeight: '141%',
              color: '#666666'
            }}
          >
            Customized interview questions and answers based on your position
          </p>
        </div>

        {/* Main Content Area */}
        <div className="flex gap-8 mb-8">
          {/* Left Side - Job Selection */}
          <div className="w-64">
            {/* Your Job Placeholder */}
            <div 
              className="w-48 h-13 rounded-xl border border-dashed mb-8 flex items-center justify-center cursor-pointer"
              style={{
                backgroundColor: '#FFFFFF',
                borderColor: '#68C6F1',
                borderRadius: '12px'
              }}
            >
              <span 
                style={{
                  fontFamily: 'Poppins',
                  fontSize: '18px',
                  fontWeight: '400',
                  color: '#282828'
                }}
              >
                Your Job
              </span>
            </div>

            {/* Examples Divider */}
            <div className="relative mb-6">
              <div 
                className="absolute inset-0 flex items-center"
                style={{ top: '11px' }}
              >
                <div 
                  className="w-full border-t"
                  style={{ 
                    borderColor: 'rgba(0, 110, 200, 0.22)',
                    borderStyle: 'dashed'
                  }}
                />
              </div>
              <div className="relative flex justify-center">
                <span 
                  className="bg-white px-4"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '16px',
                    fontWeight: '400',
                    lineHeight: '141%',
                    color: '#004B6D'
                  }}
                >
                  Examples
                </span>
              </div>
            </div>

            {/* Job Type Options */}
            <div className="space-y-3">
              {jobTypes.map((jobType, index) => (
                <div
                  key={index}
                  onClick={() => handleJobTypeSelect(jobType)}
                  className={`w-48 h-13 rounded-xl cursor-pointer flex items-center justify-center transition-colors ${
                    selectedJobType === jobType ? 'ring-2 ring-blue-500' : ''
                  }`}
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px'
                  }}
                >
                  <span 
                    style={{
                      fontFamily: 'Poppins',
                      fontSize: '15px',
                      fontWeight: '400',
                      color: '#282828'
                    }}
                  >
                    {jobType}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Right Side - Upload and Input Areas */}
          <div className="flex-1">
            <div className="flex gap-4 mb-6">
              {/* File Upload Area */}
              <div 
                className={`flex-1 h-37 rounded-2xl border border-dashed flex flex-col items-center justify-center cursor-pointer relative ${
                  loading ? 'opacity-50 pointer-events-none' : ''
                }`}
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderColor: '#77C3FF',
                  borderRadius: '16px'
                }}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                {loading ? (
                  <div className="flex flex-col items-center">
                    <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
                    <p 
                      className="text-center"
                      style={{
                        fontFamily: 'Poppins',
                        fontSize: '14px',
                        fontWeight: '400',
                        color: '#666666'
                      }}
                    >
                      Recognizing text from image...
                    </p>
                  </div>
                ) : (
                  <>
                    {/* Upload Icon */}
                    <div className="mb-4">
                  <div className="relative">
                    {/* Background rectangles */}
                    <div 
                      className="absolute w-8 h-6 rounded"
                      style={{
                        backgroundColor: '#E4EEFF',
                        top: '1px',
                        left: '10px'
                      }}
                    />
                    <div 
                      className="absolute w-10 h-8 rounded"
                      style={{
                        backgroundColor: '#C3D8FF',
                        top: '5px',
                        left: '5px'
                      }}
                    />
                    <div 
                      className="w-12 h-10 rounded-md relative"
                      style={{
                        backgroundColor: '#75A6FF',
                        borderRadius: '5px'
                      }}
                    >
                      {/* Plus icon */}
                      <div 
                        className="absolute w-5 h-5 rounded-full flex items-center justify-center"
                        style={{
                          backgroundColor: '#2F51FF',
                          right: '-10px',
                          bottom: '-10px'
                        }}
                      >
                        <svg className="w-2.5 h-2.5" style={{ color: '#FFFFFF' }} fill="currentColor" viewBox="0 0 10 10">
                          <path d="M8.75 3.75H6.25V1.25C6.25 0.5625 5.6875 0 5 0C4.3125 0 3.75 0.5625 3.75 1.25V3.75H1.25C0.5625 3.75 0 4.3125 0 5C0 5.6875 0.5625 6.25 1.25 6.25H3.75V8.75C3.75 9.4375 4.3125 10 5 10C5.6875 10 6.25 9.4375 6.25 8.75V6.25H8.75C9.4375 6.25 10 5.6875 10 5C10 4.3125 9.4375 3.75 8.75 3.75Z"/>
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
                <p 
                  className="text-center mb-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '15px',
                    fontWeight: '400',
                    color: '#282828',
                    maxWidth: '291px'
                  }}
                >
                  Drag and drop or upload a screenshot of the job description
                </p>
                <p 
                  className="text-center text-xs"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    fontWeight: '400',
                    color: '#666666',
                    maxWidth: '291px'
                  }}
                >
                  Supported formats: PNG, JPG, JPEG, BMP, TIFF, WEBP
                </p>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="mt-3 px-4 py-2 rounded-lg cursor-pointer transition-colors text-sm"
                  style={{ 
                    background: 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)',
                    color: '#383838',
                    fontFamily: 'Poppins'
                  }}
                >
                  Choose Image File
                </label>
                  </>
                )}
              </div>

              {/* URL Input Area */}
              <div 
                className="w-96 h-37 rounded-2xl border border-dashed flex flex-col items-center justify-center"
                style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.6)',
                  borderColor: '#77C3FF',
                  borderRadius: '16px'
                }}
              >
                <div className="flex items-center mb-2">
                  <div 
                    className="w-12 h-10 rounded-lg flex items-center justify-center mr-2"
                    style={{
                      backgroundColor: '#E4F5FF',
                      borderRadius: '8px'
                    }}
                  >
                    <svg className="w-7 h-7" style={{ color: '#75A6FF' }} fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.232 4.232a2.5 2.5 0 013.536 3.536l-1.225 1.224a.75.75 0 001.061 1.061l1.224-1.224a4 4 0 00-5.657-5.657l-3 3a4 4 0 00.225 5.865.75.75 0 00.977-1.138 2.5 2.5 0 01-.142-3.667l3-3z"/>
                      <path d="M11.768 19.768a2.5 2.5 0 01-3.536-3.536l1.225-1.224a.75.75 0 00-1.061-1.061l-1.224 1.224a4 4 0 005.657 5.657l3-3a4 4 0 00-.225-5.865.75.75 0 00-.977 1.138 2.5 2.5 0 01.142 3.667l-3 3z"/>
                    </svg>
                  </div>
                  <div 
                    className="px-3 py-2 rounded-lg"
                    style={{
                      backgroundColor: '#75A6FF',
                      borderRadius: '8px'
                    }}
                  >
                    <span 
                      style={{
                        fontFamily: 'Poppins',
                        fontSize: '12px',
                        fontWeight: '500',
                        lineHeight: '141%',
                        color: '#FFFFFF'
                      }}
                    >
                      Analyze
                    </span>
                  </div>
                  <div className="w-12 text-center">
                    <span 
                      style={{
                        fontFamily: 'Poppins',
                        fontSize: '12px',
                        color: '#666666'
                      }}
                    >
                      Either
                    </span>
                  </div>
                </div>
                <p 
                  className="text-center mb-1"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '15px',
                    fontWeight: '400',
                    color: '#282828'
                  }}
                >
                  Paste the job link,
                </p>
                <p 
                  className="text-center text-xs"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    fontWeight: '400',
                    color: '#666666'
                  }}
                >
                  e.g. https://www.example.com/jobs?id=abc123
                </p>
              </div>
            </div>

            {/* Job Title Input */}
            <div 
              className="w-full h-17 rounded-xl mb-4 relative"
              style={{
                backgroundColor: '#FFFFFF',
                borderRadius: '12px',
                boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)'
              }}
            >
              <div className="p-6">
                <label 
                  className="block mb-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '16px',
                    fontWeight: '400',
                    lineHeight: '141%',
                    color: '#333333'
                  }}
                >
                  Job title
                </label>
                <input
                  type="text"
                  value={jobTitle}
                  onChange={handleJobTitleChange}
                  placeholder="Please enter the job title..."
                  className="w-full border-none outline-none bg-transparent"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '14px',
                    color: '#333333'
                  }}
                  maxLength={50}
                />
                <div 
                  className="absolute bottom-6 right-6 text-xs"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    color: '#666666'
                  }}
                >
                  {jobTitle.length}/50
                </div>
              </div>
            </div>

            {/* Job Description Input */}
            <div 
              className="w-full rounded-xl relative"
              style={{
                backgroundColor: '#FFFFFF',
                borderRadius: '12px',
                boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)',
                height: '335px'
              }}
            >
              <div className="p-6 h-full flex flex-col">
                <label 
                  className="block mb-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '16px',
                    fontWeight: '400',
                    lineHeight: '141%',
                    color: '#333333'
                  }}
                >
                  Job description
                </label>
                <p 
                  className="text-xs mb-4"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    fontWeight: '400',
                    color: '#999999'
                  }}
                >
                  Copy and paste the job description here. We will generate customized questions and answers through the big model to help you improve your interview performance
                </p>
                <textarea
                  value={jobDescription}
                  onChange={handleJobDescriptionChange}
                  placeholder="Please enter the job description..."
                  className="flex-1 border border-gray-200 rounded-lg p-3 outline-none resize-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '14px',
                    color: '#333333',
                    backgroundColor: '#FAFAFA'
                  }}
                  maxLength={2000}
                />
                <div 
                  className="text-right text-xs mt-2"
                  style={{
                    fontFamily: 'Poppins',
                    fontSize: '12px',
                    color: '#666666'
                  }}
                >
                  {jobDescription.length}/2000
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <span className="text-red-700">{error}</span>
          </div>
        )}

        {/* Bottom Navigation */}
        <div className="flex justify-center space-x-6">
          {/* Home Button */}
          <button
            onClick={handleHome}
            className="flex items-center space-x-2 px-8 py-3 rounded-full transition-all duration-200"
            style={{
              backgroundColor: '#FFFFFF',
              boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)',
              opacity: 0.9
            }}
          >
            <svg className="w-5 h-5" style={{ color: '#363636' }} fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
            </svg>
            <span 
              style={{
                fontFamily: 'Poppins',
                fontSize: '20px',
                fontWeight: '400',
                color: '#363636'
              }}
            >
              Home
            </span>
          </button>

          {/* Next Button */}
          <button
            onClick={handleNext}
            disabled={!jobTitle.trim() || !jobDescription.trim()}
            className="flex items-center space-x-2 px-8 py-3 rounded-full transition-all duration-200 disabled:opacity-50"
            style={{
              background: 'linear-gradient(181deg, #9CFAFF 0%, #A3E4FF 19%, #6BBAFF 95%)',
              boxShadow: '0px 2px 8px 0px rgba(145, 215, 255, 0.2)'
            }}
          >
            <span 
              style={{
                fontFamily: 'Poppins',
                fontSize: '20px',
                fontWeight: '400',
                color: '#383838'
              }}
            >
              Next
            </span>
            <svg className="w-5 h-5" style={{ color: '#383838' }} fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobPage; 