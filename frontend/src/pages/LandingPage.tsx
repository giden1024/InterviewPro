import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom'
import './landingPage.less'
import { Collapse } from 'antd';
import { CaretRightOutlined, PlusOutlined, MinusOutlined } from '@ant-design/icons';
import logoImg from '../assets/logo.png'
import arrowRightImg from '../assets/arrow-right.png'
import secondArrowImg from '../assets/secondArrow.png'
import duihaoImg from '../assets/duihao.png'
import duihao2Img from '../assets/duihao2.png'
import emailImg from '../assets/email.png'
import microsoftImg from '../assets/microsoft.png'
import oracleImg from '../assets/oracle.png'
import walmartImg from '../assets/walmrt.png'
import macImg from '../assets/mac.png'
import amazonImg from '../assets/mazon.png'
import jpmImg from '../assets/jpm.png'
import shiduihaoImg from '../assets/shiduihao.png'
import xingqiuImg from '../assets/xingqiu.png'
import jisuanjiImg from '../assets/jisuanji.png'
import huojianImg from '../assets/huojian.png'
import shalouImg from '../assets/shalou.png'
import qaImg from '../assets/qa.png'
import user1Img from '../assets/user1.png'
import user2Img from '../assets/user2.png'
import user3Img from '../assets/user3.png'
import leftArrowImg from '../assets/leftArrow.png'
import rightArrowImg from '../assets/rightArrow.png'

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeCore, setActiveCore] = useState(0)

  const handleTabClick = (index: number) => {
    setActiveIndex(index);
  };
  const handleTabCore = (index: number) => {
    setActiveCore(index)
  }

  const tabsData = [
    { label: 'Home' },
    { label: 'Pricing' },
    { label: 'Contact Us' }
  ];
  const CoreTab = [
    { title: 'Resume Diagnosis', content: 'AI-powered resume analysis that identifies strengths and areas for improvement, helping you craft a compelling professional narrative that stands out to recruiters.' },
    { title: 'Multi-Scenario Interview Simulation', content: 'Practice with realistic interview scenarios across various industries and roles, from technical deep-dives to behavioral assessments and case studies.' },
    { title: 'Real-Time Interview Assistance', content: 'Get instant, intelligent prompts and suggestions during live interviews to help you deliver confident, well-structured responses that showcase your expertise.' }
  ];

  // Handle URL parameters for tab navigation
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const tab = urlParams.get('tab');
    if (tab === 'pricing') {
      setActiveIndex(1); // Pricing tab is index 1 in tabsData array
    } else if (tab === 'contact') {
      setActiveIndex(2); // Contact Us tab is index 2 in tabsData array
    }
  }, [location.search]);
  return (
    <div className="min-h-screen">
      <div className="offerLetterCss">
        {/* <div className="items-center nav-center"> */}
        <div className="logoImg">
          <img src={logoImg} alt="OfferOtter Logo" />
        </div>
        <div className="flex items-center  py-4">
          {/* Tab switching section */}
          {tabsData.map((tab, index) => (
            <button key={index} className={index === activeIndex ? 'active px-4' : 'px-4'} onClick={() => handleTabClick(index)}>
              {tab.label}
            </button>
          ))}
          <button
            onClick={() => navigate('/home')}
            className="px-4 py-2 bg-[#FDD985] from-[#9CFAFF] to-[#6BBAFF] text-block rounded-full  transition-all"
          >
            Get Started for Free
          </button>
        </div>
      </div>
      {/* Home section */}

      <div className={activeIndex === 0 ? "firstContent" : 'stylenone'}>
        <div className="topContent mb-8">
          <div className="mb-8">
            <h1 className="text-4xl pt-11 text-[#282828] mainFirst">
              OfferOtter Master Your Dream
            </h1>
            <h1 className=" text-4xl pt-11 text-[#282828] mainFirst">Job Interview</h1>
          </div>
          <div className="flexContent">
            <div className="Flex1 mb-4">
              <span className="flex items-center px-2.5 text-sm">Resume Diagnosis</span>
              <span className="flex items-center px-2.5 text-sm">
                <img src={secondArrowImg} style={{ width: '2.5rem' }} className="pr-2" alt="Arrow" />
                Multi-Scenario<br /> Interview <br />Simulation
              </span>
              <span className="flex items-center px-2.5 text-sm">
                <img src={secondArrowImg} style={{ width: '2.5rem' }} className="pr-2" alt="Arrow" />
                Real-Time Interview Plug-in <br />Assistance ,  Job Search Success<br /> Rate Increased by 3 Times
              </span>
            </div>
          </div>
          <div className="flexContent">
            <button
              onClick={() => navigate('/home')}
              className="px-4 py-2 bg-[#FDD985] from-[#9CFAFF] to-[#6BBAFF] text-block rounded-full  transition-all flex"
            >
              Get Started for Free&nbsp; <img src={arrowRightImg} className="arrowCss" alt="Arrow" />
            </button>
          </div>

          <div className="px-2 py-2  flex rounded-full justify-center btnCss text-sm hidden">
            <span className="text-[#0097DC]">380,000+</span>&nbsp; <span className="text-[#282828]">resumes have been analyzed, and the number of participants in simulated interviews has exceeded</span>&nbsp;<span className="text-[#0097DC]">1,200,000</span>
          </div>

          <div className="flex justify-center logoCss hidden">
            <img className="px-2.5" src={microsoftImg} alt="Microsoft" />
            <img className="px-2.5" src={oracleImg} alt="Oracle" />
            <img className="px-2.5" src={walmartImg} alt="Walmart" />
            <img className="px-2.5" src={macImg} alt="Mac" />
            <img className="px-2.5" src={amazonImg} alt="Amazon" />
            <img className="px-2.5" src={jpmImg} alt="JPM" />
          </div>
        </div>
      </div>
      {/* Tab2 section */}
      <div className={activeIndex === 1 ? "secondContent flex justify-center" : 'stylenone'}>
        <div className="content1 mr-4">
          <div className="py-2 first">
            <h4 className="text-3xl py-6">Free</h4>
            <h3 className="text-4xl py-2 font-medium">$0.00</h3>
            <p className="py-2 text-[#B7b7b7]">Monthly</p>
            <button className="bg-[#A5E2FF] text-block rounded-full px-10 py-2 mb-5">Get Started</button>
          </div>
          <div className="py-2 mb-7">
            <div className="pt-8 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Resume Analysis</p>
            </div>
            <div className="py-2 flex items-center" style={{marginBottom:'5%'}}>
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Customized Question Bank</p>
            </div>
          </div>
        </div>
        <div className="content1 mr-4 second">
          <div className="py-2 first">
            <div className="fixedText bg-white by-2 rounded-b-xl">popular</div>
            <h4 className="text-3xl py-6">PRO</h4>
            <h3 className="text-4xl py-2 font-medium">$9.99</h3>
            <p className="py-2 text-[#ffffff]">Monthly</p>
            <button className="bg-white text-block rounded-full px-10 py-2 mb-5 font-semibold">Subscribe</button>
          </div>
          <div className="py-2">
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihao2Img} alt="Check" />
              &nbsp;<p className="text-sm">999-Minute Recording Limit</p>
            </div>
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihao2Img} alt="Check" />
              &nbsp;<p className="text-sm">Mock Interview</p>
            </div>
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihao2Img} alt="Check" />
              &nbsp;<p className="text-sm">Formal Interview Assistance</p>
            </div>
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihao2Img} alt="Check" />
              &nbsp;<p className="text-sm">Resume Analysis</p>
            </div>
            <div className="py-2 flex items-center" style={{marginBottom:'5%'}}>
              <img className="tab2ContentDuihao" src={duihao2Img} alt="Check" />
              &nbsp;<p className="text-sm">Customized Question Bank</p>
            </div>
          </div>
        </div>
        <div className="content1">
          <div className="py-2 first">
            <h4 className="text-3xl py-6">Intensive</h4>
            <h3 className="text-4xl py-2 font-medium">$13.00</h3>
            <p className="py-2 text-[#B7b7b7]">Monthly</p>
            <button className="bg-[#A5E2FF] text-block rounded-full px-10 py-2 mb-5">Subscribe</button>
          </div>
          <div className="py-2">
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Unlimited Recording Limit</p>
            </div>
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Mock Interview</p>
            </div>
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Formal Interview Assistance</p>
            </div>
            <div className="py-2 pb-0 flex items-center">
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Resume Analysis</p>
            </div>
            <div className="py-2 flex items-center" style={{marginBottom:'5%'}}>
              <img className="tab2ContentDuihao" src={duihaoImg} alt="Check" />
              &nbsp;<p className="text-sm">Customized Question Bank</p>
            </div>
          </div>
        </div>
      </div>
      {/* Third section */}
      <div className={activeIndex === 2 ? "firstContent" : 'stylenone'}>
        <div className="email flex">
          <div className="flex bg-[#EEF9FF]  px-1 rounded-lg">
            <div className="flex py-2 px-1 bg-[#A5E2FF] rounded-lg text-xs items-center font-semibold">
              <img src={emailImg} alt="Email" />&nbsp;email
            </div>&nbsp;
                            <div className="flex items-center text-[#333333]">support@offerott.com</div>
          </div>
        </div>
        <div className="topContent">
          <div className="mb-8">
            <h1 className="text-4xl pt-11 text-[#282828] mainFirst">
              OfferOtter Master Your Dream
            </h1>
            <h1 className=" text-4xl pt-11 text-[#282828] mainFirst">Job Interview</h1>
          </div>
          <div className="flexContent">
            <div className="Flex1 mb-4">
              <span className="flex items-center px-2.5 text-sm">Resume Diagnosis</span>
              <span className="flex items-center px-2.5 text-sm">
                <img src={secondArrowImg} style={{ width: '2.5rem' }} className="pr-2" alt="Arrow" />
                Multi-Scenario<br /> Interview <br />Simulation
              </span>
              <span className="flex items-center px-2.5 text-sm">
                <img src={secondArrowImg} style={{ width: '2.5rem' }} className="pr-2" alt="Arrow" />
                Real-Time Interview Plug-in <br />Assistance ,  Job Search Success<br /> Rate Increased by 3 Times
              </span>
            </div>
          </div>
          <div className="flexContent">
            <button
              onClick={() => navigate('/home')}
              className="px-4 py-2 bg-[#FDD985] from-[#9CFAFF] to-[#6BBAFF] text-block rounded-full  transition-all flex"
            >
              Get Started for Free&nbsp; <img src={arrowRightImg} className="arrowCss" alt="Arrow" />
            </button>
          </div>

          <div className="px-2 py-2  flex rounded-full justify-center btnCss text-sm hidden">
            <span className="text-[#0097DC]">380,000+</span><span className="text-[#282828]">resumes have been analyzed, and the number of participants in simulated interviews has exceeded</span>&nbsp;<span className="text-[#0097DC]">1,200,000</span>
          </div>

          <div className="flex justify-center logoCss hidden">
            <img className="px-2.5" src={microsoftImg} alt="Microsoft" />
            <img className="px-2.5" src={oracleImg} alt="Oracle" />
            <img className="px-2.5" src={walmartImg} alt="Walmart" />
            <img className="px-2.5" src={macImg} alt="Mac" />
            <img className="px-2.5" src={amazonImg} alt="Amazon" />
            <img className="px-2.5" src={jpmImg} alt="JPM" />
          </div>
        </div>
      </div>
      {/* Core Features */}
      <div className="flex flex-col justify-center items-center py-10">
        <h1 className="text-4xl titleCore" style={{ marginBottom: '3%' }}>
          Core Features
        </h1>
        <div className="bg-[#EEF9FF] rounded-3xl CoreTab py-8 pt-0">
          <div className="flex justify-center items-center bottomBorder">
            {CoreTab.map((tab, index) => (
              <button key={index} className={index === activeCore ? 'font-semibold px-2 text-base' : 'px-2 text-base text-[#282828]'} onClick={() => handleTabCore(index)}>
                <span className={index === activeCore ? "icon" : 'noneIcon'}></span><br /> {tab.title}
              </button>
            ))}
          </div>
          {/* CoreTab1 */}
          <div className={activeCore === 0 ? "flex py-6 justify-center" : 'stylenone'}>
            <p className="flex items-center text-xs mr-12">
              <img src={shiduihaoImg} style={{ width: '28px', height: '28px', marginRight: '0.5rem' }} alt="Check" />
              Deep optimization: Evaluate matching through 20+ dimensions<br />
              (ATS compatibility, keyword density, achievement quantification)
            </p>
            <p className="flex items-center text-xs">
              <img src={shiduihaoImg} style={{ width: '28px', height: '28px', marginRight: '0.5rem' }} alt="Check" />
              Dynamic rewriting suggestions: Highlight problematic sentences in<br />
              real time and provide customized industry-specific scripts (such as<br />
              optimization of quantitative indicators for technical positions)
            </p>
          </div>
          <div className={activeCore === 1 ? "flex py-6 justify-center" : 'stylenone'}>
            <p className="flex items-center text-xs mr-24">
              <img src={shiduihaoImg} style={{ width: '28px', height: '28px', marginRight: '0.5rem' }} alt="Check" />
              Custom Scripts: Automatically generate position-specific<br />
              question banks and corresponding scripts (beginner to<br />
              expert-level difficulty) based on resume content.
            </p>
            <p className="flex items-center text-xs">
              <img src={shiduihaoImg} style={{ width: '28px', height: '28px', marginRight: '0.5rem' }} alt="Check" />
              Multi-dimensional Training: From business aspects to salary<br />
              negotiation; from self-introduction to experience deconstruction.<br />
              Enhance interview skills comprehensively across dimensions.
            </p>
          </div>
          <div className={activeCore === 2 ? "flex py-6 justify-center" : 'stylenone'}>
            <p className="flex items-center text-xs mr-16">
              <img src={shiduihaoImg} style={{ width: '28px', height: '28px', marginRight: '0.5rem' }} alt="Check" />
              Real-time Response Engine: Instant analysis of interviewer<br />
              questions paired with precision-matched answer scripts.
            </p>
            <p className="flex items-center text-xs">
              <img src={shiduihaoImg} style={{ width: '28px', height: '28px', marginRight: '0.5rem' }} alt="Check" />
              Crisis Intervention: Auto-Prompt Follow-Up Scripts for Silent Timeouts<br />
              and Sensitive Word Detection Alerts
            </p>
          </div>
          <div className="flex CoreContent">
            <div>{CoreTab[activeCore].content}</div>
          </div>
        </div>
      </div>

      {/* Why Choose OfferOtter */}
      <div className="flex flex-col justify-center items-center py-10">
        <h1 className="text-4xl titleCore" style={{ marginBottom: '3%' }}>
          Why Choose OfferOtter
        </h1>
        <div className="ChooseWrap">
          <div className="flex chooseOfferOtter rounded-t-3xl rounded-ee-3xl justify-between">
            <div className="flex py-6 items-center dashedSty">
              <img src={xingqiuImg} className="imgSty" alt="Star" />&nbsp;
              <div className="flex flex-col py-2">
                <h4 className="font-medium text-sm">Industry-Specific LLMs:</h4>
                <p className="text-sm">Domain-optimized models for internet, finance, FMCG,</p>
                <p className="text-sm">etc., with precise recognition of technical terminology</p>
              </div>
            </div>
            <div className="flex justify-between items-center px-4 mt-0 bg-[#A5E2FF] rounded-2xl">
              <h2 className="text-4xl px-4 font-medium">89%</h2>
              <p className="flex flex-col">
                <span><span className="font-medium text-sm">89%</span> Interview Success Rate –</span>
                <span className="flex flex-row-reverse text-sm">Surpassing industry</span>
                <span className="flex flex-row-reverse text-sm"> benchmarks by 35%</span>
              </p>
            </div>
          </div>

          <div className="flex chooseOfferOtter justify-between rounded-tr-3xl rounded-r-3xl">
            <div className="flex py-6 items-center dashedSty">
              <img src={jisuanjiImg} className="imgSty" alt="Computer" />&nbsp;
              <div className="flex flex-col py-2">
                <h4 className="font-medium text-sm">Tailored Customization:</h4>
                <p className="text-sm">Scripts and answers personalized to your resume,</p>
                <p className="text-sm">boosting interview success rates</p>
              </div>
            </div>
            <div className="flex justify-between items-center px-4 my-1 bg-[#ffffff] rounded-2xl border-2 border-solid border-[#A5E2FF]">
              <h2 className="text-4xl px-4 font-medium">95%</h2>
              <p className="flex flex-col">
                <span>
                  <span className="flex flex-row-reverse text-sm"> User Satisfaction – <span className="font-medium">95%</span>&nbsp;</span>
                </span>
                <span className="flex flex-row-reverse text-sm">Redefining career coaching standards</span>
              </p>
            </div>
          </div>

          <div className="flex chooseOfferOtter justify-between rounded-r-3xl">
            <div className="flex items-center py-6 dashedSty">
              <img src={huojianImg} className="imgSty" alt="Rocket" />&nbsp;
              <div className="flex flex-col py-2">
                <h4 className="font-medium text-sm">State-of-the-Art Recognition:</h4>
                <p className="text-sm">Industry-leading speech-to-text model with 98%</p>
                <p className="text-sm">accuracy</p>
              </div>
            </div>
            <div className="flex justify-between items-center bg-[#A5E2FF] px-4 mt-0 rounded-2xl">
              <h2 className="text-4xl px-4 font-medium">1.2M+</h2>
              <p className="flex flex-col">
                <span>
                  <span className="flex flex-row-reverse text-sm">Mock Interviews Conducted –<span className="font-medium">1.2M+</span>&nbsp;</span>
                </span>
                <span className="flex flex-row-reverse text-sm">Equivalent to 150 years of human training</span>
              </p>
            </div>
          </div>

          <div className="flex chooseOfferOtter rounded-b-3xl justify-between rounded-r-3xl" style={{ marginBottom: '5%' }}>
            <div className="flex items-center py-6">
              <img src={shalouImg} className="imgSty" alt="Hourglass" />&nbsp;
              <div className="flex flex-col py-2">
                <h4 className="font-medium text-sm">Real-Time Response:</h4>
                <p className="text-sm">200ms ultra-low latency feedback (below human</p>
                <p className="text-sm">perception threshold of 350ms)</p>
              </div>
            </div>
            <div className="flex justify-between items-center px-4 my-1 mb-0 bg-[#ffffff] rounded-2xl border-2 border-solid border-[#A5E2FF]">
              <h2 className="text-4xl px-2 font-medium">380,000</h2>
              <p className="flex flex-col">
                <span>
                  <span className="flex flex-row-reverse text-sm"> Resumes Professionally Optimized –<span className="font-medium">380,000</span>&nbsp;</span>
                </span>
                <span className="flex flex-row-reverse text-sm">Aligned with Fortune 500 hiring criteria</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Real Stories from Users */}
      <div className="flex flex-col UsersWrap items-center py-10 hidden">
        <h1 className="text-4xl titleCore" style={{ marginBottom: '8%' }}>
          Real Stories from Users
        </h1>
        <div className="flex">
          <div className="flex flex-col users">
            <p className="circle"></p>
            <div className="border-1 border-dashed userImg">
              <img src={user1Img} style={{ width: '100px' }} alt="User 1" />
            </div>
            <h2 className="font-medium py-4 UserTitle">Product Manager</h2>
            <div className="flex text-sm text-[#282828] text-center userText">
              "This platform's resume analysis helped me strategically highlight 0-to-1 product launches. The AI interviewer drilled me on balancing UX vs. monetization tradeoffs – exactly the curveball questions PM interviews throw at you! The mock PRD walkthroughs and stakeholder alignment scenarios are gold. When I cited Pirate Metrics (AARRR) to quantify feature impact, the hiring manager said, 'You've already mastered our framework.' PMs – steal their case library!"
            </div>
            <div><img src={macImg} alt="Mac" /></div>
          </div>

          <div className="flex flex-col users mx-2">
            <p className="circle"></p>
            <div className="border-1 border-dashed userImg mb-8">
              <img src={user2Img} style={{ width: '100px' }} alt="User 2" />
            </div>
            <h2 className="font-medium py-4 UserTitle">Marketing Manager</h2>
            <div className="flex justify-center text-sm text-[#282828] text-center userText">
              10 years in marketing, yet the resume audit exposed my blind spot: listing campaign metrics without proving ROI attribution or budget optimization skills. The crisis simulation? Brilliant! When the AI asked, 'How would you pivot a product launch amid a boycott?', I aced real-life scenario test. Finally transitioned from 'campaign executor' to 'growth strategist' – worth every penny!
            </div>
            <div>
              <img src={walmartImg} alt="Walmart" />
            </div>
          </div>

          <div className="flex flex-col users mx-2 ml-0">
            <p className="circle"></p>
            <div className="border-1 border-dashed userImg">
              <img src={user3Img} style={{ width: '100px' }} alt="User 3" />
            </div>
            <h2 className="font-medium py-4 UserTitle">Data Analyst</h2>
            <div className="flex justify-center text-sm text-[#282828] text-center userText">
              Stop stuffing your resume with 'built Python models'! This platform taught me to showcase business impact: 'Reduced CAC by 23% via churn-prediction models' &gt; vague tech jargon. Mock interviews crushed me (in the best way) – from defending A/B testing significance levels to explaining neural nets to CMOs. Offer in 2 weeks!
            </div>
            <div>
              <img src={oracleImg} alt="Oracle" />
            </div>
          </div>
        </div>
        <div className="flex">
          <img src={leftArrowImg} className="px-2 py-6" alt="Left Arrow" />
          <img src={rightArrowImg} className="px-4 py-6" alt="Right Arrow" />
        </div>
      </div>

      {/* FAQ Section */}
      <div className="flex flex-col items-center py-10">
        <h1 className="text-4xl titleCore">
          Any Questions
        </h1>
        <div className="text-[#0097DC] py-4 font-medium">And we have got answers to all of them</div>

        <Collapse
          bordered={false}
          defaultActiveKey={['1']}
          expandIcon={({ isActive }) => isActive ? <MinusOutlined className="pt-4" style={{ fontSize: '20px' }} /> : <PlusOutlined className="pt-4" style={{ fontSize: '20px' }} />}
          expandIconPosition="end"
          style={{ width: '70%', background: '#ffffff', position: 'relative' }}
          className="flex flex-col"
        >
          <img src={qaImg} style={{ width: '8rem', position: 'absolute', top: '-55px', left: '39px' }} alt="QA" />
          <Panel header={<div className="text-[#282828] text-sm font-semibold pt-2">What specific positions and industries is OfferOtter suitable for?</div>}
            key="1" style={{ background: '#EEF9FF', borderRadius: '30px', marginBottom: '1%', paddingLeft: '1%', paddingBottom: '1%' }}>
            <p className="pr-32">OfferOtter is a comprehensive career development platform designed specifically for recent graduates. We understand the challenges you may face when entering the workforce, so we offer a range of professional support to help you transition smoothly into your career. Whether you are a software engineer or a newcomer in any other field, OfferOtter provides professional interview guidance and industry knowledge training. We continuously optimize and expand industry-specific modules to meet the needs of various career paths.</p>
          </Panel>
          <Panel header={<div className="text-[#282828] text-sm font-semibold pt-2">Is my interview data secure?</div>} key="2"
            style={{ background: '#EEF9FF', borderRadius: '30px', marginBottom: '1%', paddingLeft: '1%', paddingBottom: '1%' }}>
            <p className="pr-32">Absolutely. We prioritize your privacy and employ advanced encryption to keep your interview data confidential. Your information is only used to enhance your experience and provide tailored responses</p>
          </Panel>
          <Panel header={<div className="text-[#282828] text-sm font-semibold pt-2">I only have weekends to prepare for the interview, how can OfferOtter help me complete it quickly?</div>}
            key="3" style={{ background: '#EEF9FF', borderRadius: '30px', marginBottom: '1%', paddingLeft: '1%', paddingBottom: '1%' }}
          >
            <p className="pr-32">87% of users complete the core preparation within 14 hours - our AI will automatically extract your job and resume and generate interview answers suitable for you. It can quickly help you complete the preparation for the upcoming interview.</p>
          </Panel>
          <Panel header={<div className="text-[#282828] text-sm font-semibold pt-2">Will you be detected using OfferOtter?</div>} key="4"
            style={{ background: '#EEF9FF', borderRadius: '30px', marginBottom: '1%', paddingLeft: '1%', paddingBottom: '1%' }}
          >
            <p className="pr-32">Not at all. We analyze the interviewer's questions in real time and present customized responses based on your personal experience. It's like having a personal coach by your side. Think of it as an assistant who helps you stand out in the interview. We have extremely low latency and will not be detected at all</p>
          </Panel>
          <Panel header={<div className="text-[#282828] text-sm font-semibold pt-2">Can OfferOtter truly understand and answer complex interview questions</div>} key="5"
            style={{ background: '#EEF9FF', borderRadius: '30px', marginBottom: '1%', paddingLeft: '1%', paddingBottom: '1%' }}>
            <p className="pr-32">Our system is meticulously engineered to deliver hyper-personalized responses by analyzing users' resumes and career narratives. Through iterative mock interview simulations, the AI progressively refines its comprehension of individual profiles, enabling granular, context-aware guidance. Crucially, the algorithm exhibits adaptive learning—with continued interaction, its output becomes increasingly synchronized with users' authentic professional trajectories. By synthesizing their unique professional journey into response generation, the AI provides nuanced, experience-driven solutions that evolve in lockstep with user growth.</p>
          </Panel>
        </Collapse>
      </div>

      {/* Final CTA Section */}
      <div className="flex flex-col sixWrap justify-center items-center rounded-full py-8">
        <div className="text-3xl text-center px-8 py-8">
          <p>OfferOtter Master Your Dream Job Interview with</p>
          <p>AI-Powered Simulation</p>
        </div>
        <div className="flex">
          <button
            onClick={() => navigate('/home')}
            className="flex px-4 py-2 bg-[#FDD985] from-[#9CFAFF] to-[#6BBAFF] text-block rounded-full transition-all px-6 mr-6"
          >
            Get Started for Free&nbsp; <img src={arrowRightImg} className="arrowCss" alt="Arrow" />
          </button>
        </div>
      </div>

      {/* Footer Section */}
      <footer className="bg-[#F8FEFF] border-t border-[#E5F4FF] py-8">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            {/* Logo and Copyright */}
            <div className="flex items-center mb-4 md:mb-0">
              <img src={logoImg} alt="OfferOtter Logo" className="h-8 w-auto mr-3" />
              <div>
                <p className="text-[#282828] font-medium">OfferOtter</p>
                <p className="text-sm text-[#666666]">© 2024 OfferOtter. All rights reserved.</p>
              </div>
            </div>

            {/* Legal Links */}
            <div className="flex space-x-6">
              <button
                onClick={() => navigate('/privacy-policy')}
                className="text-[#0097DC] hover:text-[#006FA2] text-sm font-medium transition-colors duration-200 hover:underline"
              >
                Privacy Policy
              </button>
              <span className="text-[#CCCCCC]">|</span>
              <button
                onClick={() => navigate('/terms-of-use')}
                className="text-[#0097DC] hover:text-[#006FA2] text-sm font-medium transition-colors duration-200 hover:underline"
              >
                Terms of Use
              </button>
            </div>
          </div>

          {/* Additional Footer Content */}
          <div className="mt-6 pt-6 border-t border-[#E5F4FF]">
            <div className="flex flex-col md:flex-row justify-between items-center text-sm text-[#666666]">
              <p>Master your dream job interview with AI-powered simulation</p>
              <div className="flex space-x-4 mt-3 md:mt-0">
                                  <span>📧 support@offerott.com</span>
                <span>🌍 Available worldwide</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

const { Panel } = Collapse;

export default LandingPage; 