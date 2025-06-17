import React, { useState } from 'react';

interface InterviewRecord {
  id: string;
  title: string;
  date: string;
  duration: string;
  type: 'Mock Interview' | 'Formal interview';
}

export const InterviewRecordPage: React.FC = () => {
  const [records] = useState<InterviewRecord[]>([
    {
      id: '1',
      title: 'Product Management of TikTok Live',
      date: '2025/04/16',
      duration: '1min 44sec',
      type: 'Formal interview'
    },
    {
      id: '2',
      title: 'Product Management of TikTok Live',
      date: '2025/04/16',
      duration: '1min 44sec',
      type: 'Mock Interview'
    }
  ]);

  return (
    <div className="min-h-screen bg-[#EEF9FF] flex">
      {/* Left Sidebar */}
      <div className="w-60 bg-white shadow-lg flex flex-col">
        {/* Sidebar toggle indicator */}
        <div className="absolute left-0 top-[309px] w-10 h-12 bg-[#87D2F6] rounded-r-[20px] transform -rotate-90"></div>
        
        {/* User Profile Section */}
        <div className="p-6 border-b border-gray-100">
          {/* Avatar and User Info */}
          <div className="flex items-center mb-6">
            <div className="w-9 h-9 rounded-full overflow-hidden mr-3">
              <img 
                src="https://image-resource.mastergo.com/105099925135800/105099925135802/48570855d6c32d6234b602603ee985c8.png" 
                alt="Josephine" 
                className="w-full h-full object-cover"
              />
            </div>
            <div className="flex-1">
              <h3 className="text-[13px] font-medium text-[#262626] font-poppins">Josephine</h3>
              <p className="text-xs text-[#333333] font-poppins">ID:123456</p>
            </div>
            <div className="px-3 py-1 bg-white border border-[#77C3FF] rounded-[11px] shadow-sm">
              <span className="text-xs text-[#262626] font-poppins">Free</span>
            </div>
          </div>

          {/* Time Counter */}
          <div className="bg-[#D8F0FF] border border-dashed border-[#77C3FF] rounded-lg p-4 mb-4">
            <div className="flex justify-between text-xs text-[#262626] font-poppins">
              <span>Mock x <span className="font-semibold">Min</span></span>
              <span>Formal x <span className="font-semibold">Min</span></span>
            </div>
          </div>

          {/* Upgrade Button */}
          <button className="w-full py-2 bg-gradient-to-r from-[#9CFAFF] via-[#A3E4FF] to-[#6BBAFF] rounded-full">
            <span className="text-xs font-medium text-[#262626] font-poppins">Upgrade</span>
          </button>
        </div>

        {/* Jobs Section */}
        <div className="p-6 flex-1">
          <h3 className="text-base text-[#282828] font-poppins mb-4">Jobs</h3>
          
          <div className="space-y-4">
            {/* Selected Job */}
            <div className="p-3 bg-white border border-dashed border-[#68C6F1] rounded-xl shadow-lg">
              <span className="text-base text-[#282828] font-poppins">Product Manager</span>
            </div>
            
            {/* Other Job */}
            <div className="p-3 bg-white border border-dashed border-transparent rounded-xl shadow-lg">
              <span className="text-base text-[#282828] font-poppins">Marketing Planner</span>
            </div>
          </div>

          {/* Add New Jobs */}
          <div className="mt-8 p-4 border border-dashed border-[#77C3FF] rounded-2xl bg-[#EEF9FF]">
            <div className="flex flex-col items-center">
              <div className="relative mb-3">
                {/* Layered document icons */}
                <div className="w-10 h-8 bg-[#75A6FF] rounded-sm"></div>
                <div className="absolute top-1 left-1 w-8 h-6 bg-[#C3D8FF] rounded-sm"></div>
                <div className="absolute top-2 left-2 w-6 h-4 bg-[#E4EEFF] rounded-sm"></div>
                <div className="absolute top-6 right-2 w-4 h-4 bg-[#2F51FF] rounded-full flex items-center justify-center">
                  <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                  </svg>
                </div>
              </div>
              <span className="text-[15px] font-medium text-[#282828] font-poppins">Add New Jobs</span>
            </div>
          </div>
        </div>

        {/* Mock/Formal Interview Buttons */}
        <div className="p-6 space-y-4">
          {/* Mock Interview */}
          <div className="flex items-center justify-between">
            <div className="flex flex-col items-center">
              <div className="w-24 h-24 mb-2">
                <img 
                  src="https://image-resource.mastergo.com/105099925135800/105099925135802/f4fa9a0aaa5417bc3208392a86dbde45.png"
                  alt="Mock Interview"
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="text-[15px] text-[#282828] font-poppins">Mock Interview</span>
            </div>
            <div className="w-12 h-12 bg-white/30 border border-dashed border-[#68C6F1] rounded-full flex items-center justify-center backdrop-blur-sm">
              <svg className="w-5 h-5 text-[#68C6F1]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              <svg className="w-5 h-5 text-[#68C6F1] -ml-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          </div>

          {/* Formal Interview */}
          <div className="flex items-center justify-between">
            <div className="flex flex-col items-center">
              <div className="w-27 h-26 mb-2">
                <img 
                  src="https://image-resource.mastergo.com/105099925135800/105099925135802/ae46929a901122c10783a34b2677c2db.png"
                  alt="Formal Interview"
                  className="w-full h-full object-cover"
                />
              </div>
              <span className="text-[15px] text-[#282828] font-poppins">Formal Interview</span>
            </div>
            <div className="w-12 h-12 bg-white/30 border border-dashed border-[#68C6F1] rounded-full flex items-center justify-center backdrop-blur-sm">
              <svg className="w-5 h-5 text-[#68C6F1]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
              <svg className="w-5 h-5 text-[#68C6F1] -ml-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        {/* Top placeholders */}
        <div className="flex gap-6 mb-6">
          <div className="w-[568px] h-[172px] bg-white/80 border border-dashed border-[#77C3FF] rounded-2xl"></div>
          <div className="w-[568px] h-[172px] bg-white/80 border border-dashed border-[#77C3FF] rounded-2xl"></div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6">
          {/* Question Bank Tab */}
          <div className="px-8 py-3 bg-white rounded-lg border border-[#68C6F1] border-dashed shadow-lg">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-[#68C6F1]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
              </svg>
              <span className="text-[15px] text-[#3D3D3D] font-poppins">Question Bank</span>
            </div>
          </div>

          {/* Interview Record Tab - Selected */}
          <div className="px-8 py-3 bg-white rounded-lg border border-[#68C6F1] border-dashed shadow-lg">
            <div className="flex items-center gap-2">
              <div className="w-5 h-5">
                <svg viewBox="0 0 22 22" className="w-full h-full">
                  <path fill="#68C6F1" d="M7.33333 2.0625C7.33333 3.19917 6.4075 4.125 5.27083 4.125L2.0625 4.125C1.49417 4.125 0.980833 3.89583 0.605 3.52C0.229167 3.14417 0 2.63083 0 2.0625C0 0.925833 0.925833 0 2.0625 0L5.27083 0C5.83917 0 6.3525 0.229167 6.72833 0.605C7.10417 0.980833 7.33333 1.49417 7.33333 2.0625Z"/>
                  <path fill="#68C6F1" d="M12.8883 0.0256308C13.145 0.126464 13.3833 0.263964 13.5942 0.438131C14.2542 0.978964 14.6667 1.89563 14.6667 3.3898L14.6667 12.3273C14.6667 15.0773 13.0258 15.994 11 15.994L3.66667 15.994C1.64083 15.994 0 15.0773 0 12.3273L0 3.3898C0 1.4373 0.705833 0.465631 1.76917 0.0347977C2.035 -0.0752023 2.31 0.144798 2.365 0.419798C2.49333 1.07063 2.82333 1.67563 3.3 2.1523C3.95083 2.80313 4.8125 3.16063 5.72917 3.16063L8.9375 3.16063C10.6058 3.16063 11.99 1.97813 12.3017 0.410631C12.3567 0.135631 12.6225 -0.0752025 12.8883 0.0256308ZM3.66797 7.05646L7.33464 7.05646C7.71047 7.05646 8.02214 7.36812 8.02214 7.74396C8.02214 8.11979 7.71047 8.43146 7.33464 8.43146L3.66797 8.43146C3.29214 8.43146 2.98047 8.11979 2.98047 7.74396C2.98047 7.36812 3.29214 7.05646 3.66797 7.05646ZM3.66797 12.0981C3.29214 12.0981 2.98047 11.7865 2.98047 11.4106C2.98047 11.0348 3.29214 10.7231 3.66797 10.7231L11.0013 10.7231C11.3771 10.7231 11.6888 11.0348 11.6888 11.4106C11.6888 11.7865 11.3771 12.0981 11.0013 12.0981L3.66797 12.0981Z"/>
                </svg>
              </div>
              <span className="text-[15px] text-[#3D3D3D] font-poppins">Interview Record</span>
            </div>
          </div>
        </div>

        {/* Interview Record Table */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {/* Table Header */}
          <div className="bg-[#D8F0FF] px-8 py-4 rounded-t-[10px]">
            <div className="grid grid-cols-5 gap-4">
              <div className="text-[14px] text-[#262626] font-poppins">Interview ID</div>
              <div className="text-[14px] text-[#262626] font-poppins">Date</div>
              <div className="text-[14px] text-[#262626] font-poppins">Duration</div>
              <div className="text-[14px] text-[#262626] font-poppins">Interview Type</div>
              <div className="text-[14px] text-[#262626] font-poppins">Action</div>
            </div>
          </div>

          {/* Divider */}
          <div className="h-px bg-[#E9EFFD]"></div>

          {/* Table Content */}
          <div className="p-8">
            {records.map((record, index) => (
              <React.Fragment key={record.id}>
                <div className="grid grid-cols-5 gap-4 py-4">
                  <div className="text-[14px] text-[#333333] font-poppins">{record.title}</div>
                  <div className="text-[14px] text-[#333333] font-poppins">{record.date}</div>
                  <div className="text-[14px] text-[#333333] font-poppins">{record.duration}</div>
                  <div className="text-[14px] text-[#333333] font-poppins">{record.type}</div>
                  <div>
                    <button className="text-[14px] font-medium text-[#042EFF] font-poppins hover:underline">
                      review
                    </button>
                  </div>
                </div>
                {index < records.length - 1 && (
                  <div className="h-px bg-[#E9EFFD]"></div>
                )}
              </React.Fragment>
            ))}
          </div>

          {/* Vertical divider line */}
          <div className="absolute right-[196px] top-0 w-px h-full bg-[#E9EFFD] shadow-sm"></div>
        </div>
      </div>
    </div>
  );
}; 