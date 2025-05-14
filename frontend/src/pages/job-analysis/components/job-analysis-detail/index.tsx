import { Typography, Flex, Space, Button, Tag, Tabs, Progress, List, Anchor, theme } from 'antd';
import {
  EnvironmentOutlined,
  LinkOutlined,
  CheckCircleFilled,
  AuditOutlined,
  DollarCircleOutlined,
  CloseCircleFilled
} from '@ant-design/icons';
import { useEffect, useState, useRef, useCallback } from 'react';
import { blue, green, red, yellow } from '@ant-design/colors';
import ReactMarkdown from 'react-markdown';
import { JobAnalytic } from '../../../../lib/types/job';

const { Title, Text, Paragraph } = Typography;
const { useToken } = theme;

interface JobAnalysisDetailProps {
  analytic: JobAnalytic | null;
}

const JobAnalysisDetail = ({ analytic }: JobAnalysisDetailProps) => {
  const { token } = useToken();
  const [activeTab, setActiveTab] = useState('1');
  const [activeAnchor, setActiveAnchor] = useState('general');
  const [progressAnimation, setProgressAnimation] = useState(0);
  const [containerReady, setContainerReady] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);
  const isManualScrollRef = useRef(false);
  const sectionRefs = useRef<Record<string, HTMLDivElement | null>>({});

  if (!analytic) {
    return null;
  }

  const feedbackSections = [
    {
      key: 'overall',
      title: 'Overall Assessment',
      content: analytic.overall_assessment
    },
    {
      key: 'strengths',
      title: 'Strengths',
      content: analytic.strength_details
    },
    {
      key: 'weaknesses',
      title: 'Weaknesses',
      content: analytic.weakness_concerns
    },
    {
      key: 'recommendations',
      title: 'Recommendations',
      content: analytic.recommendations
    },
    {
      key: 'questions',
      title: 'Interview Questions',
      content: analytic.questions
    },
    {
      key: 'roadmap',
      title: 'Career Roadmap',
      content: analytic.roadmap
    },
    {
      key: 'conclusion',
      title: 'Conclusion',
      content: analytic.conclusion
    }
  ].filter(section => section.content && section.content.trim().length > 0);

  useEffect(() => {
    if (activeTab === '1') {
      const timer = setTimeout(() => {
        setProgressAnimation(parseFloat((analytic.match_overall * 100).toFixed(2)));
      }, 200);
      return () => clearTimeout(timer);
    }
  }, [activeTab]);

  useEffect(() => {
    if (!containerReady) return;

    const container = contentRef.current;
    if (!container) return;

    const handleScroll = () => {
      if (isManualScrollRef.current) return;

      const sections = feedbackSections.map(section => ({
        id: section.key,
        element: document.getElementById(section.key)
      })).filter(section => section.element) as { id: string, element: HTMLElement }[];

      const scrollPosition = container.scrollTop;

      const activeSection = sections.find(section => {
        const { offsetTop, offsetHeight } = section.element;
        return scrollPosition >= offsetTop &&
          scrollPosition < offsetTop + offsetHeight;
      });

      if (activeSection) {
        setActiveAnchor(activeSection.id);
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [containerReady, feedbackSections]);

  const setContentRef = useCallback((node: HTMLDivElement) => {
    contentRef.current = node;
    if (node) {
      setContainerReady(true);
    }
  }, []);

  const getMatchScoreColor = (score: number) => {
    if (score >= 75) return green.primary;
    if (score >= 50) return blue.primary;
    if (score >= 25) return yellow[5];
    return red.primary;
  };

  const handleAnchorClick = (link: { href: string }) => {
    const anchorKey = link.href.replace('#', '');
    isManualScrollRef.current = true;

    setActiveAnchor(anchorKey);
    document.getElementById(anchorKey)?.scrollIntoView({
      behavior: 'smooth',
      block: 'start'
    });

    setTimeout(() => {
      isManualScrollRef.current = false;
    }, 500);
  };

  const items = [
    {
      key: '1',
      label: 'Matching Analysis',
      children: (
        <Flex vertical style={{ padding: '0 16px' }}>
          <Flex vertical>
            <div style={{ marginTop: 4, fontWeight: 500 }}>Overall</div>
            <Progress
              percent={progressAnimation}
              strokeColor={getMatchScoreColor((analytic.match_overall * 100))}
              status="active"
            />
            <Text>
              {analytic.match_overall * 100 > 75 ? 'Excellent match for your profile!' :
                analytic.match_overall * 100 > 50 ? 'Good match for your profile' :
                  analytic.match_overall * 100 > 25 ? 'Moderate match for your profile' :
                    'Consider improving your skills or looking for better matches'}
            </Text>
            <Flex vertical justify="space-between" style={{ marginTop: 20 }}>
              {analytic.match_skills > 0 && (
                <div style={{ textAlign: 'start', minWidth: 100, marginRight: 16 }}>
                  <div style={{ marginTop: 4, fontWeight: 500 }}>Semantic Score</div>
                  <Progress
                    percent={analytic.match_skills * 100}
                    strokeColor={getMatchScoreColor(analytic.match_skills * 100)}
                    status="active"
                  />
                </div>
              )}
              {analytic.match_experience > 0 && (
                <div style={{ textAlign: 'start', marginRight: 16 }}>
                  <div style={{ marginTop: 4, fontWeight: 500 }}>LLM Score</div>
                  <Progress
                    percent={parseFloat((analytic.match_experience * 100).toFixed(2))}
                    strokeColor={getMatchScoreColor(analytic.match_experience * 100)}
                    status="active"
                  />
                </div>
              )}
            </Flex>
          </Flex>

          <Flex justify="space-between" style={{ marginTop: 16 }}>
            <Flex vertical style={{ flex: 1 }}>
              <Title level={4} style={{ color: token.colorSuccessActive, margin: 0 }}>Strengths</Title>
              <List
                dataSource={analytic.strengths.split('<br>')}
                split={false}
                renderItem={(item) => (
                  <Space size="small" style={{ width: '100%', marginBottom: 8 }}>
                    <CheckCircleFilled style={{ color: token.colorSuccess, fontSize: 16 }} />
                    <Text>{item}</Text>
                  </Space>
                )}
                style={{
                  padding: '8px 0',
                }}
              />
            </Flex>

            <Flex vertical style={{ flex: 1 }}>
              <Title level={4} style={{ color: token.colorErrorActive, margin: 0 }}>Weaknesses</Title>
              <List
                itemLayout="horizontal"
                dataSource={analytic.weaknesses.split('<br>')}
                split={false}
                renderItem={(item) => (
                  <Space size="small" style={{ width: '100%', marginBottom: 8 }}>
                    <CloseCircleFilled style={{ color: token.colorError, fontSize: 16 }} />
                    <Text>{item}</Text>
                  </Space>
                )}
                style={{
                  padding: '8px 0',
                }}
              />
            </Flex>
          </Flex>
        </Flex>
      ),
    },
    {
      key: '2',
      label: 'AI Report',
      children: (
        <Flex style={{ height: '60vh', width: '100%' }} className="scrollbar-custom container">
          <Flex
            style={{
              width: 180,
              borderRight: `1px solid ${token.colorBorderSecondary}`,
              overflowY: 'auto'
            }}
          >
            <Anchor
              affix={false}
              direction="vertical"
              items={feedbackSections.map(section => ({
                key: section.key,
                href: `#${section.key}`,
                title: section.title,
              }))}
              onClick={(e, link) => {
                e.preventDefault();
                handleAnchorClick({ href: link.href });
              }}
              getCurrentAnchor={() => {
                return `#${activeAnchor}`;
              }}
              getContainer={() => contentRef.current as HTMLElement}
            />
          </Flex>

          <Flex
            vertical
            style={{
              flex: 1,
              padding: '0 16px',
              overflowY: 'auto'
            }}
            ref={setContentRef}
            className="content"
          >
            {feedbackSections.map((section) => (
              <div
                key={section.key}
                id={section.key}
                style={{ scrollMarginTop: 16 }}
                ref={(el) => {
                  sectionRefs.current[section.key] = el;
                }}
                data-section
              >
                <ReactMarkdown
                  components={{
                    h1: ({ ...props }) => <Title level={2} {...props} />,
                    h2: ({ ...props }) => <Title level={3} {...props} style={{ marginTop: 0 }} />,
                    h3: ({ ...props }) => <Title level={4} {...props} />,
                    p: ({ ...props }) => <Paragraph {...props} />,
                    ul: ({ ...props }) => <ul style={{ paddingLeft: 16 }} {...props} />,
                    li: ({ ...props }) => <li style={{ marginBottom: 4 }} {...props} />
                  }}
                >
                  {section.content}
                </ReactMarkdown>
              </div>
            ))}
          </Flex>
        </Flex>
      )
    }
  ];

  return (
    <Flex vertical>
      <Flex vertical>
        <Title level={3} style={{ margin: 0 }}>{analytic.job_name}</Title>
        <Space>
          <Text type="secondary" style={{ fontSize: 16, fontWeight: 600 }}>{analytic.company_name}</Text>
          <Button
            type="text"
            icon={<LinkOutlined />}
            href={analytic.job_url}
            target="_blank"
            style={{
              color: token.colorPrimary,
            }}
          >
            Apply
          </Button>
        </Space>
      </Flex>

      <Flex vertical gap="middle" wrap="wrap" style={{ marginTop: 8 }}>
        <Space size="small">
          <Space>
            <EnvironmentOutlined />
            {analytic.location || 'Remote'}
          </Space>
          {analytic.job_type && (
            <Space>
              <AuditOutlined />
              {analytic.job_type}
            </Space>
          )}
          {analytic.benefit && analytic.benefit.includes('$') && (
            <Space>
              <DollarCircleOutlined />
              {analytic.benefit}
            </Space>
          )}
        </Space>
        {/* <Space>
          <SettingOutlined />
          <span>Analyzed on {analytic.analyzedAt.toLocaleString()}</span>
        </Space> */}
        <Space wrap>
          {analytic.skills && analytic.skills.split(',').map((skill, index) => (
            <Tag key={index} color={token.colorInfoBg} style={{ padding: '2px 8px', fontSize: 12, borderRadius: 8, borderColor: token.colorInfoBorder }}>
              <Text style={{ color: token.colorInfoActive }}>{skill}</Text>
            </Tag>
          ))}
        </Space>
      </Flex>

      <Tabs
        defaultActiveKey="1"
        items={items}
        onChange={setActiveTab}
        tabBarStyle={{ marginTop: 16 }}
        style={{
          alignItems: 'center',
        }}
      />
    </Flex>
  );
};

export default JobAnalysisDetail;
