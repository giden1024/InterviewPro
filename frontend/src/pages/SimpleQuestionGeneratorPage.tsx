import React, { useState } from 'react';
import { Upload, Button, Card, List, Typography, Alert, Spin, message } from 'antd';
import { UploadOutlined, FileTextOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import type { UploadFile, UploadProps } from 'antd';
import { questionService, SimpleQuestion, SimpleGenerateResponse } from '../services/questionService';

const { Title, Text, Paragraph } = Typography;
const { Dragger } = Upload;

// 使用questionService中定义的接口，这里保留是为了兼容性
interface GeneratedQuestion {
  id: number;
  question: string;
  type?: string;
}

const SimpleQuestionGeneratorPage: React.FC = () => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState<GeneratedQuestion[]>([]);
  const [resumeText, setResumeText] = useState<string>('');
  const [error, setError] = useState<string>('');

  const uploadProps: UploadProps = {
    name: 'resume',
    multiple: false,
    accept: '.pdf',
    fileList,
    beforeUpload: (file) => {
      // 验证文件类型
      const isPDF = file.type === 'application/pdf';
      if (!isPDF) {
        message.error('只支持PDF格式的简历文件！');
        return false;
      }

      // 验证文件大小（限制为10MB）
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('文件大小不能超过10MB！');
        return false;
      }

      setFileList([file]);
      return false; // 阻止自动上传
    },
    onRemove: () => {
      setFileList([]);
      setQuestions([]);
      setResumeText('');
      setError('');
    },
  };

  const generateQuestions = async () => {
    if (fileList.length === 0) {
      message.error('请先上传简历文件！');
      return;
    }

    setLoading(true);
    setError('');
    setQuestions([]);

    try {
      // 使用questionService的简化问题生成方法
      const file = fileList[0] as any;
      const data: SimpleGenerateResponse = await questionService.simpleGenerateQuestions(file);

      if (data.success && data.data?.questions) {
        setQuestions(data.data.questions);
        setResumeText(data.data.resume_text || '');
        message.success(`成功生成 ${data.data.questions.length} 个面试问题！`);
      } else {
        setError(data.error || '生成问题失败');
        message.error(data.error || '生成问题失败');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '网络错误，请稍后重试';
      setError(errorMessage);
      message.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* 页面标题 */}
        <div className="text-center mb-8">
          <Title level={2} className="text-gray-800">
            <QuestionCircleOutlined className="mr-3 text-blue-500" />
            智能面试问题生成器
          </Title>
          <Paragraph className="text-gray-600 text-lg">
            上传您的简历，AI将为您生成10个精准的面试问题
          </Paragraph>
        </div>

        {/* 文件上传区域 */}
        <Card className="mb-6 shadow-sm">
          <Title level={4} className="mb-4">
            <FileTextOutlined className="mr-2" />
            步骤1：上传简历文件
          </Title>
          <Dragger {...uploadProps} className="p-6">
            <p className="ant-upload-drag-icon">
              <UploadOutlined className="text-4xl text-blue-500" />
            </p>
            <p className="ant-upload-text text-lg font-medium">
              点击或拖拽PDF简历文件到此区域上传
            </p>
            <p className="ant-upload-hint text-gray-500">
              支持PDF格式，文件大小不超过10MB
            </p>
          </Dragger>

          {fileList.length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <Text strong className="text-blue-700">
                已选择文件：{fileList[0].name}
              </Text>
              <Text className="text-gray-600 ml-4">
                ({(fileList[0].size! / 1024 / 1024).toFixed(2)} MB)
              </Text>
            </div>
          )}
        </Card>

        {/* 生成按钮 */}
        <div className="text-center mb-6">
          <Button
            type="primary"
            size="large"
            onClick={generateQuestions}
            loading={loading}
            disabled={fileList.length === 0}
            className="px-8 py-6 h-auto text-lg font-medium"
          >
            {loading ? '正在生成问题...' : '生成面试问题'}
          </Button>
        </div>

        {/* 错误提示 */}
        {error && (
          <Alert
            message="生成失败"
            description={error}
            type="error"
            showIcon
            className="mb-6"
          />
        )}

        {/* 加载状态 */}
        {loading && (
          <Card className="text-center py-8 mb-6">
            <Spin size="large" />
            <div className="mt-4">
              <Text className="text-lg text-gray-600">
                AI正在分析您的简历并生成面试问题...
              </Text>
            </div>
          </Card>
        )}

        {/* 简历文本预览 */}
        {resumeText && (
          <Card className="mb-6 shadow-sm">
            <Title level={4} className="mb-4">解析的简历内容预览</Title>
            <div className="bg-gray-50 p-4 rounded-lg max-h-40 overflow-y-auto">
              <Text className="text-sm text-gray-700 whitespace-pre-wrap">
                {resumeText.substring(0, 500)}
                {resumeText.length > 500 && '...'}
              </Text>
            </div>
          </Card>
        )}

        {/* 生成的问题列表 */}
        {questions.length > 0 && (
          <Card className="shadow-sm">
            <Title level={4} className="mb-4">
              <QuestionCircleOutlined className="mr-2 text-green-500" />
              生成的面试问题 ({questions.length}个)
            </Title>
            <List
              dataSource={questions}
              renderItem={(question, index) => (
                <List.Item className="border-b border-gray-100 last:border-b-0 py-4">
                  <div className="w-full">
                    <div className="flex items-start">
                      <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-medium mr-4">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <Text className="text-lg text-gray-800 leading-relaxed">
                          {question.question}
                        </Text>
                        {question.type && (
                          <div className="mt-2">
                            <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                              {question.type}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* 使用说明 */}
        <Card className="mt-8 bg-blue-50 border-blue-200">
          <Title level={5} className="text-blue-800 mb-3">使用说明</Title>
          <ul className="text-blue-700 space-y-2">
            <li>• 请确保上传的PDF文件清晰可读，包含完整的个人信息、工作经历和技能</li>
            <li>• AI会根据您的简历内容生成针对性的面试问题</li>
            <li>• 生成的问题涵盖技术能力、工作经验、项目经历等多个方面</li>
            <li>• 建议提前准备这些问题的答案，提高面试成功率</li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default SimpleQuestionGeneratorPage;
