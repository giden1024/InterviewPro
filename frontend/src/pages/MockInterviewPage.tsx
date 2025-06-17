import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface InterviewQuestion {
  id: string;
  question: string;
  answer: string;
  timestamp: string;
}

interface InterviewSession {
  currentQuestion: string;
  responses: InterviewQuestion[];
  isRecording: boolean;
  autoScroll: boolean;
  timer: number;
}

export const MockInterviewPage: React.FC = () => {
  const navigate = useNavigate();
  
  const [session, setSession] = useState<InterviewSession>({
    currentQuestion: "How would you measure the success of a live streamer recruitment campaign?​​",
    responses: [
      {
        id: '1',
        question: 'Please introduce yourself',
        answer: 'To tackle stigma, I\'d focus on reframing live streaming as a tool for ​​community empowerment​​ rather than just entertainment. For example, in Indonesia, I\'d partner with local religious leaders or educators to launch a campaign like \'Knowledge Live,\' where respected figures (e.g., Quran teachers, traditional artisans) demonstrate how streaming helps them share skills or preserve culture. To incentivize participation, I\'d create a \'First Stream Kit\'—offering free lighting filters and halal-compliant',
        timestamp: '01:32'
      },
      {
        id: '2',
        question: 'What is the biggest challenge you have encountered?',
        answer: 'To tackle stigma, I\'d focus on reframing live streaming as a tool for ​​community empowerment​​ rather than just entertainment. For example, in Indonesia, I\'d partner with local religious leaders or educators to launch a campaign like \'Knowledge Live,\' where respected figures (e.g., Quran teachers, traditional artisans) demonstrate how streaming helps them share skills or preserve culture. To incentivize participation, I\'d create a \'First Stream Kit\'—offering free lighting filters and halal-compliant',
        timestamp: '01:32'
      }
    ],
    isRecording: false,
    autoScroll: true,
    timer: 0
  });

  // Timer effect
  useEffect(() => {
    const timer = setInterval(() => {
      setSession(prev => ({ ...prev, timer: prev.timer + 1 }));
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // const formatTime = (seconds: number): string => {
  //   const mins = Math.floor(seconds / 60);
  //   const secs = seconds % 60;
  //   return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  // };

  const handleLeave = () => {
    navigate('/');
  };

  const toggleAutoScroll = () => {
    setSession(prev => ({ ...prev, autoScroll: !prev.autoScroll }));
  };

  const handleRegenerate = (responseId: string) => {
    // Logic to regenerate response
    console.log('Regenerate response:', responseId);
  };

  const handleLike = (responseId: string) => {
    console.log('Like response:', responseId);
  };

  const handleDislike = (responseId: string) => {
    console.log('Dislike response:', responseId);
  };

  return (
    <div className="min-h-screen bg-[#EEF9FF] flex">
      {/* Top Header */}
      <div className="absolute top-0 left-0 right-0 h-[72px] bg-white shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] z-10 flex items-center justify-between px-6">
        {/* Offerotter Logo */}
        <div className="flex items-center space-x-2">
          <div className="w-9 h-9">
            <div 
              className="w-full h-full bg-cover bg-center"
              style={{
                backgroundImage: `url('https://image-resource.mastergo.com/105099925135800/105099925135802/48570855d6c32d6234b602603ee985c8.png')`
              }}
            />
          </div>
          <span className="text-[11.58px] font-bold text-[#A07161] font-poppins">Offerotter</span>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center space-x-4">
          {/* Settings */}
          <button className="w-8 h-8 bg-white border border-dashed border-[#EEEEEE] rounded-md flex items-center justify-center hover:bg-gray-50 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" className="text-[#393939]">
              <path fill="currentColor" d="M16.45 3.8089C15.55 5.3789 16.29 6.6589 18.1 6.6589C19.15 6.6589 20 7.5189 20.01 8.5589L20.01 10.3189C20.01 11.3689 19.15 12.2189 18.11 12.2189C16.3 12.2189 15.56 13.4989 16.47 15.0689C16.99 15.9689 16.68 17.1389 15.77 17.6589L14.04 18.6489C13.25 19.1189 12.23 18.8389 11.76 18.0489L11.65 17.8589C10.74 16.2889 9.26 16.2889 8.36 17.8589L8.25 18.0489C7.78 18.8389 6.76 19.1189 5.97 18.6489L4.24 17.6589C3.33 17.1389 3.02 15.9789 3.54 15.0689C4.45 13.4989 3.71 12.2189 1.9 12.2189C0.85 12.2189 0 11.3589 0 10.3189L0 8.5589C0 7.5089 0.86 6.6589 1.9 6.6589C3.71 6.6589 4.45 5.3789 3.54 3.8189C3.02 2.9089 3.33 1.7389 4.24 1.2189L5.97 0.228901C6.76 -0.241099 7.78 0.0389014 8.23 0.828901L8.34 1.0189C9.25 2.5889 10.73 2.5889 11.63 1.0189L11.74 0.828901C12.21 0.0389014 13.23 -0.241099 14.02 0.228901L15.75 1.2189C16.66 1.7389 16.97 2.8989 16.45 3.8089ZM6.75 9.4389C6.75 11.2289 8.21 12.6889 10 12.6889C11.79 12.6889 13.25 11.2289 13.25 9.4389C13.25 7.6489 11.79 6.1889 10 6.1889C8.21 6.1889 6.75 7.6489 6.75 9.4389Z"/>
            </svg>
          </button>

          {/* Microphone */}
          <button className="w-8 h-8 bg-white border border-dashed border-[#EEEEEE] rounded-md flex items-center justify-center hover:bg-gray-50 transition-colors">
            <svg width="24" height="24" viewBox="0 0 24 24" className="text-[#393939]">
              <path fill="currentColor" d="M5.53846 0C2.48103 0 0 2.48755 0 5.55301L0 11.9855C0 15.0509 2.48103 17.5385 5.53846 17.5385C8.59589 17.5385 11.0769 15.0509 11.0769 11.9855L11.0769 5.55301C11.0769 2.48755 8.59589 0 5.53846 0Z" transform="translate(6.46, 0.92)"/>
              <path fill="currentColor" d="M14.94 0.0100002C14.55 0.0100002 14.24 0.32 14.24 0.71L14.24 2.29C14.24 5.83 11.36 8.71 7.82 8.71C4.28 8.71 1.4 5.83 1.4 2.29L1.4 0.700001C1.4 0.310001 1.09 0 0.7 0C0.31 0 0 0.310001 0 0.700001L0 2.28C0 6.35 3.13 9.7 7.12 10.06L7.12 12.19C7.12 12.58 7.43 12.89 7.82 12.89C8.21 12.89 8.52 12.58 8.52 12.19L8.52 10.06C12.5 9.71 15.64 6.35 15.64 2.28L15.64 0.700001C15.63 0.320001 15.32 0.0100002 14.94 0.0100002Z" transform="translate(4.18, 10.96)"/>
            </svg>
          </button>

          {/* Leave Button */}
          <button 
            onClick={handleLeave}
            className="bg-white border border-dashed border-[#EEEEEE] rounded-[38px] px-4 py-2 flex items-center space-x-2 hover:bg-gray-50 transition-colors"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" className="text-[#F16868]">
              <path fill="currentColor" d="M0 10C0 4.48 4.48 0 10 0C15.53 0 20 4.48 20 10C20 15.52 15.52 20 10 20C4.48 20 0 15.52 0 10ZM11.26 14.23C12.92 14.23 14.26 12.89 14.26 11.23L14.26 8.77C14.26 7.11 12.92 5.77 11.26 5.77L8.8 5.77C7.14 5.77 5.8 7.11 5.8 8.77L5.8 11.23C5.8 12.89 7.14 14.23 8.8 14.23L11.26 14.23Z" transform="translate(1.97, 2)"/>
            </svg>
            <span className="text-[15px] text-[#3D3D3D] font-poppins">Leave</span>
          </button>
        </div>
      </div>

      {/* Left Sidebar - Character */}
      <div className="w-60 bg-white rounded-xl mt-24 mb-6 ml-6 shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] flex flex-col">
        {/* Character Avatar */}
        <div className="p-6 flex-1 flex flex-col items-center justify-center">
          <div className="w-54 h-33 mb-4">
            <div 
              className="w-full h-full bg-cover bg-center rounded-lg"
              style={{
                backgroundImage: `url('https://image-resource.mastergo.com/105099925135800/105099925135802/2bdeb680edd5a221e7f1aad022b83a46.png')`
              }}
            />
          </div>
          <h3 className="text-base font-semibold text-[#282828] mb-2 font-poppins">Interviewer says</h3>
          <div className="w-6 h-1.5 bg-[#87D2F6] rounded-full"></div>
        </div>

        {/* Interview Questions */}
        <div className="p-6 space-y-4 border-t border-gray-100">
          {/* Question 1 */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <svg width="24" height="24" viewBox="0 0 24 24" className="text-[#6FBDFF]">
                <path fill="currentColor" d="M15 0L5 0C2 0 0 2 0 5L0 11C0 14 2 16 5 16L5 18.13C5 18.93 5.89 19.41 6.55 18.96L11 16L15 16C18 16 20 14 20 11L20 5C20 2 18 0 15 0ZM10.75 8.73C10.75 8.45 10.87 8.28 11.26 8.02C11.57 7.81 12.41 7.24 12.41 6.1C12.41 4.77 11.33 3.69 10 3.69C8.67 3.69 7.59 4.77 7.59 6.1C7.59 6.51 7.93 6.85 8.34 6.85C8.75 6.85 9.09 6.51 9.09 6.1C9.09 5.6 9.5 5.19 10 5.19C10.5 5.19 10.91 5.6 10.91 6.1C10.91 6.36 10.79 6.53 10.42 6.78C10.1 7 9.25 7.57 9.25 8.73L9.25 8.94C9.25 9.35 9.59 9.69 10 9.69C10.41 9.69 10.75 9.35 10.75 8.94L10.75 8.73ZM10 12.17C9.58 12.17 9.25 11.83 9.25 11.42C9.25 11.01 9.58 10.67 10 10.67C10.42 10.67 10.75 11.01 10.75 11.42C10.75 11.83 10.42 12.17 10 12.17Z"/>
              </svg>
              <span className="text-xs text-[#999999] font-poppins">01:23</span>
            </div>
            <div className="bg-white border border-dashed border-[#EEEEEE] rounded-lg p-4">
              <p className="text-xs text-[#282828] font-poppins">Please introduce yourself</p>
            </div>
          </div>

          {/* Question 2 */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2">
              <svg width="24" height="24" viewBox="0 0 24 24" className="text-[#6FBDFF]">
                <path fill="currentColor" d="M15 0L5 0C2 0 0 2 0 5L0 11C0 14 2 16 5 16L5 18.13C5 18.93 5.89 19.41 6.55 18.96L11 16L15 16C18 16 20 14 20 11L20 5C20 2 18 0 15 0ZM10.75 8.73C10.75 8.45 10.87 8.28 11.26 8.02C11.57 7.81 12.41 7.24 12.41 6.1C12.41 4.77 11.33 3.69 10 3.69C8.67 3.69 7.59 4.77 7.59 6.1C7.59 6.51 7.93 6.85 8.34 6.85C8.75 6.85 9.09 6.51 9.09 6.1C9.09 5.6 9.5 5.19 10 5.19C10.5 5.19 10.91 5.6 10.91 6.1C10.91 6.36 10.79 6.53 10.42 6.78C10.1 7 9.25 7.57 9.25 8.73L9.25 8.94C9.25 9.35 9.59 9.69 10 9.69C10.41 9.69 10.75 9.35 10.75 8.94L10.75 8.73ZM10 12.17C9.58 12.17 9.25 11.83 9.25 11.42C9.25 11.01 9.58 10.67 10 10.67C10.42 10.67 10.75 11.01 10.75 11.42C10.75 11.83 10.42 12.17 10 12.17Z"/>
              </svg>
              <span className="text-xs text-[#999999] font-poppins">01:23</span>
            </div>
            <div className="bg-white border border-dashed border-[#EEEEEE] rounded-lg p-4">
              <p className="text-xs text-[#282828] font-poppins">What is the biggest challenge you have encountered?</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 mx-6 mt-24 mb-6">
        <div className="bg-white rounded-xl h-full shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] flex flex-col">
          {/* Section Headers */}
          <div className="p-6 border-b border-gray-100">
            <div className="flex items-center space-x-8">
              {/* Interview Copilot */}
              <div className="flex items-center space-x-2">
                <div className="w-6 h-1.5 bg-[#87D2F6] rounded-full"></div>
                <h2 className="text-base font-semibold text-[#282828] font-poppins">Interview Copilot</h2>
                
                {/* Auto Scroll Toggle */}
                <div className="flex items-center space-x-2 ml-8">
                  <button 
                    onClick={toggleAutoScroll}
                    className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                      session.autoScroll ? 'bg-[#2F51FF]' : 'bg-gray-300'
                    }`}
                  >
                    <div className={`w-4 h-4 rounded-full bg-white transition-transform ${
                      session.autoScroll ? 'translate-x-0' : '-translate-x-1'
                    }`}></div>
                  </button>
                  <span className="text-[15px] text-[#3D3D3D] font-poppins">Auto Scroll</span>
                </div>
              </div>
            </div>
          </div>

          {/* Interview Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            <div className="space-y-6">
              {session.responses.map((response, index) => (
                <div key={response.id} className="space-y-4">
                  {/* Response Content */}
                  <div className="space-y-2">
                    <p className="text-[15px] text-[#333333] leading-relaxed font-poppins">
                      {response.answer}
                    </p>
                    
                    {/* Response Controls */}
                    <div className="flex items-center justify-between">
                      <span className="text-[15px] text-[#999999] font-poppins">{response.timestamp}</span>
                      
                      <div className="flex items-center space-x-3">
                        {/* Regenerate Button */}
                        <button 
                          onClick={() => handleRegenerate(response.id)}
                          className="bg-white border border-dashed border-[#EEEEEE] rounded-md px-4 py-2 flex items-center space-x-2 hover:bg-gray-50 transition-colors"
                        >
                          <svg width="20" height="20" viewBox="0 0 20 20" className="text-[#25282B]">
                            <path fill="currentColor" d="M16.0254 6.10969Q15.4525 4.49374 14.1708 3.35459Q12.8876 2.21408 11.2132 1.83521Q9.53872 1.45634 7.88954 1.93337Q7.47237 2.05404 7.08307 2.22188Q5.93824 2.71545 5.03442 3.61696Q5.03056 3.62081 5.02672 3.62465Q5.01748 3.63389 5.00796 3.64284L4.99868 3.65155L1.14129 7.27617L0 6.06158L1.21459 4.92029L3.85739 2.43696Q5.37139 0.92676 7.42644 0.332335Q8.31278 0.0759593 9.20497 0.0173617Q9.86907 -0.0262562 10.5364 0.0397099Q11.0577 0.091239 11.581 0.209635Q13.674 0.683218 15.278 2.10886Q16.2433 2.96683 16.887 4.04117Q17.3129 4.752 17.5979 5.55755L16.0267 6.11354L16.0254 6.10969L16.0254 6.10969ZM15.6174 14.234L18.2602 11.7507L19.4748 10.6094L18.3335 9.39483L17.1189 10.5361L14.4761 13.0194L14.4668 13.0282Q14.4573 13.0371 14.448 13.0464Q14.4444 13.05 14.4404 13.054Q14.2923 13.2017 14.1378 13.3384Q13.0283 14.3202 11.5852 14.7376Q10.0391 15.1848 8.47079 14.8798Q8.36625 14.8595 8.26159 14.8358Q6.58714 14.4569 5.30394 13.3164Q4.10095 12.2472 3.5224 10.7579Q3.48406 10.6592 3.44845 10.5586L3.44804 10.5575L1.87685 11.1135Q2.1619 11.919 2.58777 12.6298Q3.23142 13.7042 4.19672 14.5621Q5.70047 15.8987 7.63406 16.3984Q7.76298 16.4318 7.89378 16.4614Q9.72522 16.8758 11.5325 16.471Q11.7906 16.4132 12.0483 16.3387Q14.1034 15.7442 15.6174 14.234Z"/>
                          </svg>
                          <span className="text-[15px] text-[#3D3D3D] font-poppins">regenerate</span>
                        </button>

                        {/* Like/Dislike Buttons */}
                        <div className="flex items-center space-x-2">
                          <button 
                            onClick={() => handleLike(response.id)}
                            className="text-[#999999] hover:text-[#6FBDFF] transition-colors"
                          >
                            <svg width="20" height="20" viewBox="0 0 20 20">
                              <path fill="currentColor" d="M12 3C12 2.20435 11.6839 1.44129 11.1213 0.87868C10.5587 0.316071 9.79565 0 9 0L6 6.75L6 20L16.28 20C16.7623 20.0055 17.2304 19.8364 17.5979 19.524C17.9654 19.2116 18.2077 18.7769 18.28 18.3L19.66 9.3C19.7035 9.01336 19.6842 8.72068 19.6033 8.44225C19.5225 8.16382 19.3821 7.90629 19.1919 7.68751C19.0016 7.46873 18.7661 7.29393 18.5016 7.17522C18.2371 7.0565 17.9499 6.99672 17.66 7L12 7L12 3ZM2 9L4 9L4 20L2 20C1.46957 20 0.960859 19.7893 0.585786 19.4142C0.210714 19.0391 0 18.5304 0 18L0 11C0 10.4696 0.210714 9.96086 0.585786 9.58579C0.960859 9.21071 1.46957 9 2 9Z"/>
                            </svg>
                          </button>
                          <button 
                            onClick={() => handleDislike(response.id)}
                            className="text-[#999999] hover:text-[#F16868] transition-colors"
                          >
                            <svg width="20" height="20" viewBox="0 0 20 20" className="rotate-180">
                              <path fill="currentColor" d="M12 3C12 2.20435 11.6839 1.44129 11.1213 0.87868C10.5587 0.316071 9.79565 0 9 0L6 6.75L6 20L16.28 20C16.7623 20.0055 17.2304 19.8364 17.5979 19.524C17.9654 19.2116 18.2077 18.7769 18.28 18.3L19.66 9.3C19.7035 9.01336 19.6842 8.72068 19.6033 8.44225C19.5225 8.16382 19.3821 7.90629 19.1919 7.68751C19.0016 7.46873 18.7661 7.29393 18.5016 7.17522C18.2371 7.0565 17.9499 6.99672 17.66 7L12 7L12 3ZM2 9L4 9L4 20L2 20C1.46957 20 0.960859 19.7893 0.585786 19.4142C0.210714 19.0391 0 18.5304 0 18L0 11C0 10.4696 0.210714 9.96086 0.585786 9.58579C0.960859 9.21071 1.46957 9 2 9Z"/>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Divider */}
                  {index < session.responses.length - 1 && (
                    <div className="w-full border-t border-dashed border-[rgba(0,110,200,0.22)]"></div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Right Sidebar - Question Bank */}
      <div className="w-[411px] bg-white rounded-xl mt-24 mb-6 mr-6 shadow-[0px_2px_8px_0px_rgba(145,215,255,0.2)] flex flex-col">
        {/* Question Bank Header */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center space-x-2">
            <div className="w-6 h-1.5 bg-[#87D2F6] rounded-full"></div>
            <h2 className="text-base font-semibold text-[#282828] font-poppins">Question Bank</h2>
          </div>
        </div>

        {/* Current Question */}
        <div className="p-6 flex-1">
          <h3 className="text-lg font-semibold text-[#333333] mb-4 leading-tight font-poppins">
            {session.currentQuestion}
          </h3>
          
          <div className="space-y-4">
            <p className="text-[15px] text-[#333333] leading-relaxed font-poppins">
              Quality of adoption​​: % of new streamers who complete ≥3 streams (measuring retention, not just interest).
              Sentiment shift​​: Pre/post-campaign surveys on perceptions (e.g., 'Is streaming a respectable career?').
              Efficiency​​: Cost-per-engaged-streamer (CPES), factoring in training/resources provided.
              For example, if we recruit 1,000 streamers but only 200 stay active after a month, I'd investigate pain points (e.g., monetization clarity) and iterate. I'd also benchmark against local competitors' retention rates to contextualize results.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MockInterviewPage; 