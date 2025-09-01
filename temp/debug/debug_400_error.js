const API_BASE = 'http://localhost:5001/api/v1';
const TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc1NDIwNjUxMCwianRpIjoiOTQxNTM0YjktYWVlMy00M2FkLWE3MDEtZThmNmM2YjNiNGVjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjMiLCJuYmYiOjE3NTQyMDY1MTAsImV4cCI6MTc1NDI5MjkxMH0.-1Hbpd611zDWqcSRWNUKMmDE6W-7OVlsmJxpEvOVbcc';

async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${TOKEN}`
        },
        ...options
    };

    console.log(`🔗 API Call: ${options.method || 'GET'} ${url}`);
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        console.log(`📊 Response Status: ${response.status}`);
        console.log(`📋 Response Data:`, JSON.stringify(data, null, 2));
        
        if (!response.ok) {
            console.error(`❌ API Error: ${response.status} - ${data.error?.message || data.message || 'Unknown error'}`);
            return { error: data, status: response.status };
        }
        
        return { data, status: response.status };
    } catch (error) {
        console.error(`💥 Network Error:`, error.message);
        throw error;
    }
}

async function testMockInterviewStart() {
    console.log('🧪 开始测试Mock Interview Start 400错误...\n');
    
    try {
        // 1. 获取简历
        console.log('📄 步骤1: 获取简历列表');
        const resumeResult = await apiCall('/resumes');
        if (resumeResult.error) return;
        
        const resumes = resumeResult.data.data.resumes;
        const processedResume = resumes.find(r => r.status === 'processed');
        
        if (!processedResume) {
            console.log('❌ 没有找到已处理的简历');
            return;
        }
        
        console.log(`✅ 找到简历 ID: ${processedResume.id}\n`);

        // 2. 创建面试会话
        console.log('🎯 步骤2: 创建面试会话');
        const sessionResult = await apiCall('/interviews', {
            method: 'POST',
            body: JSON.stringify({
                resume_id: processedResume.id,
                interview_type: 'mock',
                total_questions: 5,
                custom_title: '400错误调试测试'
            })
        });
        
        if (sessionResult.error) return;
        
        const sessionId = sessionResult.data.data.session_id;
        const initialStatus = sessionResult.data.data.session.status;
        console.log(`✅ 会话创建成功 ID: ${sessionId}`);
        console.log(`📊 初始状态: ${initialStatus}\n`);

        // 3. 生成问题
        console.log('❓ 步骤3: 生成面试问题');
        const questionResult = await apiCall('/questions/generate', {
            method: 'POST',
            body: JSON.stringify({
                resume_id: processedResume.id,
                session_id: sessionId,
                interview_type: 'mock',
                total_questions: 5
            })
        });
        
        if (questionResult.error) return;
        
        const afterGenStatus = questionResult.data.data.session.status;
        console.log(`✅ 问题生成成功，共 ${questionResult.data.data.questions.length} 个`);
        console.log(`📊 问题生成后状态: ${afterGenStatus}\n`);

        // 4. 获取会话详情
        console.log('🔍 步骤4: 获取会话详情');
        const sessionDetailResult = await apiCall(`/interviews/${sessionId}`);
        if (sessionDetailResult.error) return;
        
        const currentStatus = sessionDetailResult.data.data.status;
        console.log(`📊 当前会话状态: ${currentStatus}\n`);

        // 5. 第一次启动面试（应该成功）
        console.log('🚀 步骤5: 第一次启动面试');
        const startResult1 = await apiCall(`/interviews/${sessionId}/start`, {
            method: 'POST'
        });
        
        if (startResult1.error) {
            console.log(`❌ 第一次启动失败: ${startResult1.error.error?.message || startResult1.error.message}`);
        } else {
            console.log(`✅ 第一次启动成功，状态: ${startResult1.data.data.status}`);
        }

        // 6. 第二次启动面试（应该失败）
        console.log('\n🔄 步骤6: 第二次启动面试（模拟重复调用）');
        const startResult2 = await apiCall(`/interviews/${sessionId}/start`, {
            method: 'POST'
        });
        
        if (startResult2.error) {
            console.log(`❌ 第二次启动失败（预期行为）: ${startResult2.error.error?.message || startResult2.error.message}`);
            console.log(`📊 错误状态码: ${startResult2.status}`);
        } else {
            console.log(`⚠️ 第二次启动意外成功: ${startResult2.data.data.status}`);
        }

        console.log('\n📈 测试总结:');
        console.log(`- 初始状态: ${initialStatus}`);
        console.log(`- 生成问题后: ${afterGenStatus}`);
        console.log(`- 当前状态: ${currentStatus}`);
        console.log(`- 第一次启动: ${startResult1.error ? '失败' : '成功'}`);
        console.log(`- 第二次启动: ${startResult2.error ? '失败（预期）' : '成功（异常）'}`);

    } catch (error) {
        console.error('💥 测试过程中发生错误:', error);
    }
}

// 运行测试
testMockInterviewStart(); 