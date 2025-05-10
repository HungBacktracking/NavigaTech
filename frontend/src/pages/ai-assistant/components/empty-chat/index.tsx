import { Typography, theme, Flex, Card } from 'antd';
import { RobotOutlined, SendOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

interface EmptyChatProps {
  onSelectSamplePrompt: (prompt: string) => void;
  samplePrompts: string[];
}

const EmptyChat = ({ onSelectSamplePrompt, samplePrompts = [] }: EmptyChatProps) => {
  const { token } = theme.useToken();

  const handleSelectPrompt = (prompt: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    onSelectSamplePrompt(prompt);
  };

  const defaultPrompts = [
    "How to build a standout resume for a frontend developer role?",
    "What questions should I prepare for a Java developer interview?",
    "How can I improve my LinkedIn profile to attract recruiters?",
    "What skills are in high demand for data science positions?"
  ];

  const displayPrompts = samplePrompts.length > 0 ? samplePrompts : defaultPrompts;

  return (
    <Flex
      align="center"
      justify="center"
      style={{
        height: '100%',
        padding: '20px'
      }}
    >
      <Flex
        vertical
        align="center"
        style={{
          maxWidth: '700px',
          animation: 'fadeIn 0.5s ease-out'
        }}
        className="fadeInAnimation"
      >
        <Flex
          align="center"
          justify="center"
          style={{
            marginBottom: '24px',
            backgroundColor: token.colorPrimaryBg,
            borderRadius: '50%',
            width: '80px',
            height: '80px',
          }}
        >
          <RobotOutlined style={{ fontSize: '36px', color: token.colorPrimary }} />
        </Flex>

        <Title level={3}>JobTinder AI Assistant</Title>

        <Text
          style={{
            fontSize: '16px',
            marginBottom: '40px',
            color: token.colorTextSecondary,
            maxWidth: '600px',
            textAlign: 'center'
          }}
        >
          Your personal AI assistant to help with job searching, resume preparation,
          interview preparation, and career advice.
        </Text>

        <Flex vertical style={{ width: '100%', marginBottom: '40px' }}>
          <Title level={5} style={{ textAlign: 'center' }}>Try asking about:</Title>

          <Flex wrap="wrap" gap="middle" justify="center" style={{ marginTop: '16px' }}>
            {displayPrompts.map((prompt, index) => (
              <Card
                key={index}
                hoverable
                style={{
                  width: 280,
                  backgroundColor: token.colorFillQuaternary,
                  borderColor: token.colorBorderSecondary,
                  cursor: 'pointer',
                  position: 'relative',
                  paddingRight: '30px'
                }}
                onClick={handleSelectPrompt(prompt)}
                className="exampleItem"
              >
                {prompt}
                <SendOutlined
                  style={{
                    position: 'absolute',
                    bottom: '12px',
                    right: '12px',
                    color: token.colorPrimary
                  }}
                />
              </Card>
            ))}
          </Flex>
        </Flex>
      </Flex>
    </Flex>
  );
};

export default EmptyChat;