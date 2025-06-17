import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobService, Job, JobTemplate, CreateJobData } from '../services/jobService';

const JobPage: React.FC = () => {
  const navigate = useNavigate();
  
  // 状态管理
  const [activeTab, setActiveTab] = useState<'create' | 'browse' | 'templates'>('browse');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [templates, setTemplates] = useState<JobTemplate[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  
  // 创建职位表单状态
  const [createForm, setCreateForm] = useState<CreateJobData>({
    title: '',
    company: '',
    description: '',
    location: '',
    job_type: 'full-time',
    requirements: [],
    skills_required: [],
    experience_level: 'mid'
  });
  
  // URL解析状态
  const [jobUrl, setJobUrl] = useState('');
  const [urlAnalyzing, setUrlAnalyzing] = useState(false);
  
  // 搜索和过滤状态
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('active');

  // 页面加载时获取数据
  useEffect(() => {
    loadJobs();
    loadTemplates();
  }, []);

  // 加载职位列表
  const loadJobs = async () => {
    try {
      setLoading(true);
      const response = await jobService.getJobs({
        status: statusFilter,
        search: searchQuery,
        per_page: 20
      });
      setJobs(response.jobs);
    } catch (err) {
      setError('加载职位失败');
      console.error('加载职位失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 加载职位模板
  const loadTemplates = async () => {
    try {
      const templateList = await jobService.getJobTemplates();
      setTemplates(templateList);
    } catch (err) {
      console.error('加载模板失败:', err);
    }
  };

  // 创建职位
  const handleCreateJob = async () => {
    if (!createForm.title.trim()) {
      setError('请输入职位标题');
      return;
    }

    try {
      setLoading(true);
      const newJob = await jobService.createJob(createForm);
      setJobs([newJob, ...jobs]);
      setSelectedJob(newJob);
      setCreateForm({
        title: '',
        company: '',
        description: '',
        location: '',
        job_type: 'full-time',
        requirements: [],
        skills_required: [],
        experience_level: 'mid'
      });
      setActiveTab('browse');
      setError('');
    } catch (err) {
      setError('创建职位失败');
      console.error('创建职位失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 分析职位URL
  const handleAnalyzeUrl = async () => {
    if (!jobUrl.trim()) {
      setError('请输入职位URL');
      return;
    }

    try {
      setUrlAnalyzing(true);
      const result = await jobService.analyzeJobUrl(jobUrl);
      setJobs([result.job, ...jobs]);
      setSelectedJob(result.job);
      setJobUrl('');
      setActiveTab('browse');
      setError('');
    } catch (err) {
      setError('URL分析失败，请检查链接是否有效');
      console.error('URL分析失败:', err);
    } finally {
      setUrlAnalyzing(false);
    }
  };

  // 使用模板创建职位
  const handleUseTemplate = async (template: JobTemplate) => {
    setCreateForm({
      title: template.title,
      company: '',
      description: template.description,
      location: '',
      job_type: 'full-time',
      requirements: [],
      skills_required: template.skills,
      experience_level: template.experience_level
    });
    setActiveTab('create');
  };

  // 选择职位进入下一步
  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
    navigate('/resume', {
      state: {
        jobTitle: job.title,
        jobDescription: job.description,
        jobId: job.id,
        company: job.company,
        requirements: job.requirements,
        skills: job.skills_required
      }
    });
  };

  // 搜索职位
  const handleSearch = () => {
    loadJobs();
  };

  return (
    <div className="min-h-screen bg-blue-50 py-12">
      <div className="container mx-auto px-6 max-w-7xl">
        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-12">
          <div className="bg-white rounded-full px-8 py-4 shadow-lg flex items-center space-x-16">
            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-blue-100 border-2 border-gray-600 border-dashed rounded-full flex items-center justify-center">
                <svg className="w-4 h-4 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 2L8 4h4l-2-2zM6 6v8h8V6H6z"/>
                </svg>
              </div>
              <span className="text-blue-800 text-lg font-semibold">Job</span>
            </div>

            <div className="w-9 h-9 bg-gray-100 bg-opacity-50 border-2 border-gray-800 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-lg">
              <svg className="w-4 h-4 text-gray-800" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5l5 5-5 5V5z"/>
              </svg>
            </div>

            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-gray-100 bg-opacity-50 border-2 border-gray-800 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-lg">
                <svg className="w-4 h-4 text-gray-800" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 5l5 5-5 5V5z"/>
                </svg>
              </div>
              <span className="text-gray-600 text-lg">Resume</span>
            </div>

            <div className="w-9 h-9 bg-gray-50 bg-opacity-60 border-2 border-gray-400 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-md">
              <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 5l5 5-5 5V5z"/>
              </svg>
            </div>

            <div className="flex items-center space-x-4">
              <div className="w-9 h-9 bg-gray-50 bg-opacity-60 border-2 border-gray-400 border-dashed rounded-full flex items-center justify-center backdrop-blur-sm shadow-md">
                <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
              </div>
              <span className="text-gray-400 text-lg">Complete</span>
            </div>
          </div>
        </div>

        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-medium text-gray-800 mb-4">
            Which job interview are you preparing for?
          </h1>
          <p className="text-gray-600">
            Browse existing jobs, create new ones, or analyze job postings from URLs
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
              </svg>
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-sm">
            <button
              onClick={() => setActiveTab('browse')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'browse'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Browse Jobs ({jobs.length})
            </button>
            <button
              onClick={() => setActiveTab('create')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'create'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Create Job
            </button>
            <button
              onClick={() => setActiveTab('templates')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'templates'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Templates ({templates.length})
            </button>
          </div>
        </div>

        {/* Browse Tab */}
        {activeTab === 'browse' && (
          <div className="space-y-6">
            {/* Search and Filter */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search jobs by title, company, or description..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  />
                </div>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="active">Active Jobs</option>
                  <option value="all">All Jobs</option>
                  <option value="archived">Archived</option>
                </select>
                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>

            {/* URL Analysis */}
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Analyze Job URL</h3>
              <div className="flex gap-4">
                <input
                  type="url"
                  value={jobUrl}
                  onChange={(e) => setJobUrl(e.target.value)}
                  placeholder="Paste job posting URL here (e.g., from Indeed, LinkedIn, etc.)"
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={handleAnalyzeUrl}
                  disabled={urlAnalyzing || !jobUrl.trim()}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center space-x-2"
                >
                  {urlAnalyzing ? (
                    <>
                      <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                      </svg>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M12.232 4.232a2.5 2.5 0 013.536 3.536l-1.225 1.224a.75.75 0 001.061 1.061l1.224-1.224a4 4 0 00-5.657-5.657l-3 3a4 4 0 00.225 5.865.75.75 0 00.977-1.138 2.5 2.5 0 01-.142-3.667l3-3z"/>
                      </svg>
                      <span>Analyze</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Paste a job posting URL and we'll automatically extract the job details for you.
              </p>
            </div>

            {/* Jobs List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {loading && jobs.length === 0 ? (
                <div className="col-span-full text-center py-12">
                  <svg className="animate-spin w-8 h-8 text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                  </svg>
                  <p className="text-gray-600">Loading jobs...</p>
                </div>
              ) : jobs.length === 0 ? (
                <div className="col-span-full text-center py-12">
                  <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2h8zM16 10h.01M12 14h.01M8 14h.01M8 10h.01"/>
                  </svg>
                  <h3 className="text-lg font-medium text-gray-800 mb-2">No jobs found</h3>
                  <p className="text-gray-600 mb-4">Create your first job or try a different search.</p>
                  <button
                    onClick={() => setActiveTab('create')}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Create Job
                  </button>
                </div>
              ) : (
                jobs.map((job) => (
                  <div
                    key={job.id}
                    className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow cursor-pointer border border-gray-100"
                    onClick={() => handleSelectJob(job)}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="text-lg font-medium text-gray-800 line-clamp-2">{job.title}</h3>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        job.job_type === 'full-time' ? 'bg-green-100 text-green-800' :
                        job.job_type === 'part-time' ? 'bg-blue-100 text-blue-800' :
                        job.job_type === 'contract' ? 'bg-purple-100 text-purple-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {job.job_type}
                      </span>
                    </div>
                    
                    {job.company && (
                      <p className="text-gray-600 mb-2 flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-6a1 1 0 00-1-1H9a1 1 0 00-1 1v6a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd"/>
                        </svg>
                        {job.company}
                      </p>
                    )}
                    
                    {job.location && (
                      <p className="text-gray-600 mb-3 flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
                        </svg>
                        {job.location}
                      </p>
                    )}
                    
                    {job.description && (
                      <p className="text-gray-600 text-sm line-clamp-3 mb-3">
                        {job.description}
                      </p>
                    )}
                    
                    {job.skills_required && job.skills_required.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {job.skills_required.slice(0, 3).map((skill, index) => (
                          <span key={index} className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded">
                            {skill}
                          </span>
                        ))}
                        {job.skills_required.length > 3 && (
                          <span className="px-2 py-1 bg-gray-50 text-gray-600 text-xs rounded">
                            +{job.skills_required.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                    
                    <div className="flex justify-between items-center text-sm text-gray-500">
                      <span>{new Date(job.created_at).toLocaleDateString()}</span>
                      {job.match_score && (
                        <span className="text-green-600 font-medium">
                          {job.match_score}% match
                        </span>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Create Tab */}
        {activeTab === 'create' && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-xl p-8 shadow-sm">
              <h2 className="text-xl font-medium text-gray-800 mb-6">Create New Job</h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    value={createForm.title}
                    onChange={(e) => setCreateForm({...createForm, title: e.target.value})}
                    placeholder="e.g., Senior Software Engineer"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company
                  </label>
                  <input
                    type="text"
                    value={createForm.company}
                    onChange={(e) => setCreateForm({...createForm, company: e.target.value})}
                    placeholder="e.g., Tech Corp"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      value={createForm.location}
                      onChange={(e) => setCreateForm({...createForm, location: e.target.value})}
                      placeholder="e.g., San Francisco, CA"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Job Type
                    </label>
                    <select
                      value={createForm.job_type}
                      onChange={(e) => setCreateForm({...createForm, job_type: e.target.value as any})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="full-time">Full Time</option>
                      <option value="part-time">Part Time</option>
                      <option value="contract">Contract</option>
                      <option value="internship">Internship</option>
                      <option value="freelance">Freelance</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Experience Level
                  </label>
                  <select
                    value={createForm.experience_level}
                    onChange={(e) => setCreateForm({...createForm, experience_level: e.target.value})}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="entry">Entry Level</option>
                    <option value="mid">Mid Level</option>
                    <option value="senior">Senior Level</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Description
                  </label>
                  <textarea
                    value={createForm.description}
                    onChange={(e) => setCreateForm({...createForm, description: e.target.value})}
                    placeholder="Describe the role, responsibilities, and requirements..."
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Provide a detailed description to help generate better interview questions.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Required Skills (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={createForm.skills_required?.join(', ') || ''}
                    onChange={(e) => setCreateForm({
                      ...createForm, 
                      skills_required: e.target.value.split(',').map(s => s.trim()).filter(s => s)
                    })}
                    placeholder="e.g., JavaScript, React, Node.js, Python"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div className="flex justify-end space-x-4 pt-4">
                  <button
                    onClick={() => setActiveTab('browse')}
                    className="px-6 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateJob}
                    disabled={loading || !createForm.title.trim()}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
                  >
                    {loading ? 'Creating...' : 'Create Job'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {templates.map((template) => (
              <div
                key={template.id}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100"
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-medium text-gray-800">{template.title}</h3>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                    {template.category}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-4">{template.description}</p>
                
                <div className="flex flex-wrap gap-1 mb-4">
                  {template.skills.slice(0, 4).map((skill, index) => (
                    <span key={index} className="px-2 py-1 bg-gray-50 text-gray-700 text-xs rounded">
                      {skill}
                    </span>
                  ))}
                  {template.skills.length > 4 && (
                    <span className="px-2 py-1 bg-gray-50 text-gray-600 text-xs rounded">
                      +{template.skills.length - 4} more
                    </span>
                  )}
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500 capitalize">
                    {template.experience_level} level
                  </span>
                  <button
                    onClick={() => handleUseTemplate(template)}
                    className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Use Template
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Bottom Navigation */}
        <div className="flex justify-center space-x-6 mt-12">
          <button
            onClick={() => navigate('/')}
            className="bg-white text-gray-700 px-8 py-3 rounded-full font-medium text-lg transition-all duration-200 shadow-md hover:shadow-lg flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
            </svg>
            <span>Home</span>
          </button>

          {selectedJob && (
            <button
              onClick={() => handleSelectJob(selectedJob)}
              className="px-8 py-3 rounded-full font-medium text-lg transition-all duration-200 shadow-lg bg-gradient-to-r from-blue-400 to-blue-600 hover:from-blue-500 hover:to-blue-700 text-white hover:shadow-xl flex items-center space-x-2"
            >
              <span>Continue with "{selectedJob.title}"</span>
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd"/>
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobPage; 