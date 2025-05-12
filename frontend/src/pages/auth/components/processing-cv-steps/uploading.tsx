import { Upload, Button, Typography, theme, Flex, message } from 'antd';
import { UploadOutlined, FilePdfOutlined } from '@ant-design/icons';
import type { RcFile, UploadProps } from 'antd/es/upload';
import { useState } from 'react';

const { Text } = Typography;

interface UploadStepProps {
  onUpload: (file: File) => Promise<void>;
}

const UploadStep = ({ onUpload }: UploadStepProps) => {
  const { token } = theme.useToken();
  const [fileList, setFileList] = useState<any[]>([]);
  const [uploading, setUploading] = useState(false);

  const beforeUpload = (file: RcFile) => {
    const isPDF = file.type === 'application/pdf';
    if (!isPDF) {
      message.error('You can only upload PDF files!');
      return false;
    }

    const isLt5M = file.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('File must be smaller than 5MB!');
      return false;
    }

    return true;
  };

  const handleChange: UploadProps['onChange'] = (info) => {
    setFileList(info.fileList.slice(-1));
  };

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.error('Please select a file to upload');
      return;
    }

    setUploading(true);
    try {
      await onUpload(fileList[0].originFileObj);
      setUploading(false);
    } catch (error) {
      console.error('Upload failed:', error);
      message.error('Failed to upload CV. Please try again.');
      setUploading(false);
    }
  };

  return (
    <Flex vertical align="center" style={{ width: '100%', gap: '1rem' }}>
      <Upload
        beforeUpload={beforeUpload}
        onChange={handleChange}
        fileList={fileList}
        maxCount={1}
        accept=".pdf"
        listType="picture"
        style={{ width: '100%' }}
        itemRender={(originNode) => (
          <div style={{
            maxWidth: '360px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {originNode}
          </div>
        )}
      >
        <Button
          size="large"
          style={{
            height: '200px',
            borderRadius: 16,
            border: `1px dashed ${token.colorBorder}`,
            display: 'flex',
            flexDirection: 'column',
            width: '100%',
          }}
        >
          <FilePdfOutlined style={{ fontSize: 40, marginBottom: 8 }} />
          <Text>Click or drag file to this area to upload</Text>
          <Text type="secondary">English resumes in PDF only. Max 5MB file size.</Text>
        </Button>
      </Upload>

      <Button
        type="primary"
        icon={<UploadOutlined />}
        onClick={handleUpload}
        loading={uploading}
        disabled={fileList.length === 0 || uploading}
        size="large"
        style={{ borderRadius: 50, padding: '0.5rem 3rem' }}
      >
        Upload
      </Button>
    </Flex>
  );
};

export default UploadStep;