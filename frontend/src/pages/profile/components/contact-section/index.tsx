import React from 'react';
import { Typography, Flex, Card, theme } from 'antd';
import { PhoneOutlined, MailOutlined, LinkedinOutlined, GithubOutlined, LinkedinFilled, GithubFilled, MailFilled, PhoneFilled } from '@ant-design/icons';

const { Title, Text } = Typography;

interface ContactInfoSectionProps {
  email: string;
  phoneNumber: string;
  linkedin: string;
  github: string;
}

const ContactInfoSection: React.FC<ContactInfoSectionProps> = ({
  email,
  phoneNumber,
  linkedin,
  github,
}) => {
  const { token } = theme.useToken();

  return (
    <Card
      variant='borderless'
      title={<Title level={4} style={{ margin: 0 }}>Contact Information</Title>}
      style={{ marginBottom: 24, borderRadius: 8 }}
    >
      <Flex vertical gap={12}>
        <Flex align="center">
          <MailFilled style={{ marginRight: 8, fontSize: '16px', color: token.colorError }} />
          {
            email ? 
              <a href={`mailto:${email}`} target="_blank" rel="noopener noreferrer">{email}</a> :
              <Text>Add your email address</Text>
          }
        </Flex>
        <Flex align="center">
          <PhoneFilled style={{ marginRight: 8, fontSize: '16px', color: token.colorSuccess }} />
          {
            phoneNumber ? 
              <a href={`tel:${phoneNumber}`} target="_blank" rel="noopener noreferrer">{phoneNumber}</a> : 
              <Text>Add your phone number</Text>
          }
        </Flex>
        <Flex align="center">
          <LinkedinFilled style={{ marginRight: 8, fontSize: '16px', color: token['blue-6'] }} />
          {
            linkedin ? 
              <a href={linkedin} target="_blank" rel="noopener noreferrer">{linkedin}</a> : 
              <Text>Add your LinkedIn profile</Text>
          }
        </Flex>
        <Flex align="center">
          <GithubFilled style={{ marginRight: 8, fontSize: '16px', color: 'black' }} />
          {
            github ? 
              <a href={github} target="_blank" rel="noopener noreferrer">{github}</a> : 
              <Text>Add your GitHub profile</Text>
          }
        </Flex>
      </Flex>
    </Card>
  );
};

export default ContactInfoSection;