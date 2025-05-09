import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';
import {
  Button,
  Tooltip,
  Typography,
  Flex,
  Divider,
  Table,
  theme
} from 'antd';
import { CopyOutlined, CheckOutlined, CodeOutlined } from '@ant-design/icons';

import { PrismAsyncLight as SyntaxHighlighter } from 'react-syntax-highlighter';
import { SyntaxHighlighterProps } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useState } from 'react';
import { ColumnsType } from 'antd/es/table';
import { blueDark } from '@ant-design/colors';

const { Text, Title, Paragraph } = Typography;
const SyntaxHighlighterComponent = SyntaxHighlighter as React.ComponentType<SyntaxHighlighterProps>;

export interface CustomMarkdownProps {
  content: string;
  id?: string;
}

const CustomMarkdown = ({ content, id }: CustomMarkdownProps) => {
  const { token } = theme.useToken();
  const [selectedCopiedCode, setSelectedCopiedCode] = useState<string | null>(null);
  const copyCodeToClipboard = (code: string, codeId: string) => {
    navigator.clipboard.writeText(code);
    setSelectedCopiedCode(codeId);
    setTimeout(() => setSelectedCopiedCode(null), 2000);
  };
  

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeRaw]}
      components={{
        h1: ({ node, ...props }) => <Title level={1} {...props} />,
        h2: ({ node, ...props }) => <Title level={2} {...props} />,
        h3: ({ node, ...props }) => <Title level={3} {...props} />,
        h4: ({ node, ...props }) => <Title level={4} {...props} />,
        h5: ({ node, ...props }) => <Title level={5} {...props} />,
        h6: ({ node, ...props }) => <Title level={5} {...props} />,
        p: ({ node, ...props }) => <Paragraph {...props} />,
        a: ({ node, href, ...props }) => (
          <a href={href} target="_blank" rel="noopener noreferrer" {...props} />
        ),
        blockquote: ({ node, ...props }) => (
          <blockquote
            style={{
              margin: '16px 0',
              padding: '0 16px',
              borderLeft: `4px solid ${token.colorBorder}`,
              color: token.colorTextSecondary,
            }}
            {...props}
          />
        ),
        ul: ({ node, ...props }) => <ul style={{ paddingLeft: '8px' }} {...props} />,
        ol: ({ node, ...props }) => <ol style={{ paddingLeft: '8px' }} {...props} />,
        li: ({ node, ...props }) => <li style={{ marginBottom: '8px' }} {...props} />,
        hr: () => <Divider />,
        code: ({ node, className, children, ...props }) => {
          const match = /language-(\w+)/.exec(className || '');
          const language = match ? match[1] : '';
          const codeStr = String(children).replace(/\n$/, '');
          const codeId = `${id ?? 'code-id'}-${language}-${codeStr.substring(0, 5)}`;

          if (match) {
            return (
              <Flex
                vertical
              >
                <Flex
                  horizontal
                  justify="space-between"
                  align="center"
                  style={{
                    padding: '8px 16px',
                    backgroundColor: '#343a40',
                    borderRadius: '8px 8px 0 0',
                  }}
                >
                  <div style={{ display: 'flex', color: '#d4d4d4' }}>
                    <CodeOutlined style={{ marginRight: '8px' }} />
                    <Text style={{ color: '#d4d4d4' }}>
                      {language || 'code'}
                    </Text>
                  </div>
                  <Tooltip title={(selectedCopiedCode === codeId) ? "Code copied!" : "Copy code"} color={blueDark[2]}>
                    <Button
                      type="text"
                      icon={(selectedCopiedCode === codeId) ? <CheckOutlined style={{ color: token.colorSuccess }} /> : <CopyOutlined style={{ color: '#d4d4d4' }} />}
                      onClick={() => copyCodeToClipboard(codeStr, codeId)}
                      size="small"
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                    />
                  </Tooltip>
                </Flex>
                <SyntaxHighlighterComponent
                  language={language}
                  style={vscDarkPlus}
                  showLineNumbers
                  customStyle={{
                    borderRadius: '0 0 8px 8px',
                    margin: 0,
                  }}
                >
                  {codeStr}
                </SyntaxHighlighterComponent>
              </Flex>
            );
          }
          return (
            <Typography style={{ backgroundColor: token.colorFillSecondary, padding: '8px', borderRadius: '8px' }}>
              <Text
                style={{
                  fontFamily: 'monospace',
                }}
                {...props}
              >
                {codeStr}
              </Text>
            </Typography>
          );
        },
        table: ({ node, ...props }) => {
          const columns: ColumnsType<any> = [];
          const data: any[] = [];

          if (!node) return (
            <div {...props} />
          );

          if (node.children && node.children.length > 0) {
            const headerRow = node.children[0];
            if (headerRow && headerRow.type === 'element' && headerRow.tagName === 'thead') {
              const headerCells = headerRow.children?.[0]?.children || [];
              headerCells.forEach((cell: any, index: number) => {
                const cellContent = cell.children?.[0]?.value || `Column ${index + 1}`;
                columns.push({
                  title: cellContent,
                  dataIndex: `column${index}`,
                  key: `column${index}`,
                });
              });
            }

            const bodyRows = node.children[1]?.children || [];
            bodyRows.forEach((row: any, rowIndex: number) => {
              const rowData: any = { key: rowIndex };
              if (row.children) {
                row.children.forEach((cell: any, cellIndex: number) => {
                  let cellValue = '';

                  if (cell.children && cell.children.length > 0) {
                    const firstChild = cell.children[0];
                    if (firstChild.type === 'text') {
                      cellValue = firstChild.value || '';
                    } else if (firstChild.value !== undefined) {
                      cellValue = firstChild.value;
                    } else if (typeof firstChild === 'string') {
                      cellValue = firstChild;
                    }
                  }

                  rowData[`column${cellIndex}`] = cellValue;
                });
                data.push(rowData);
              }
            });
          }

          return (
            <Table
              columns={columns}
              dataSource={data}
              pagination={false}
              bordered
            />
          );
        },
        thead: ({ node, ...props }) => {
          return <thead
            style={{
              backgroundColor: token.colorFillSecondary,
              borderBottom: `2px solid ${token.colorBorderSecondary}`
            }}
            {...props}
          />;
        },
        tbody: ({ node, ...props }) => {
          return <tbody {...props} />;
        },
        tr: ({ node, ...props }) => {
          return <tr {...props} />;
        },
        th: ({ node, ...props }) => {
          return (
            <th style={{
              padding: '12px 16px',
              borderBottom: `1px solid ${token.colorBorderSecondary}`,
              textAlign: 'left',
              fontWeight: 600,
              backgroundColor: token.colorFillSecondary
            }} {...props} />
          );
        },
        td: ({ node, ...props }) => {
          return (
            <td style={{
              padding: '12px 16px',
              borderBottom: `1px solid ${token.colorBorderSecondary}`
            }} {...props} />
          );
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
};

export default CustomMarkdown;