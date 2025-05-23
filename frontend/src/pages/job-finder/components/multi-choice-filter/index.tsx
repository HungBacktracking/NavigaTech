import { Dropdown, Button, Space, Tag, Typography, Flex, Spin, theme } from 'antd';
import { DownOutlined, CloseOutlined, CheckOutlined } from '@ant-design/icons';
import { MouseEvent, useState } from 'react';

const { Text } = Typography;

export interface FilterOption {
  value: string;
  label: string;
}

interface MultiChoiceFilterProps {
  label: string;
  options: FilterOption[];
  selectedValues: string[];
  onChange: (selectedValues: string[]) => void;
  isLoading?: boolean;
}

const MultiChoiceFilter = ({
  label,
  options,
  selectedValues,
  onChange,
  isLoading = false,
}: MultiChoiceFilterProps) => {
  const [tempSelectedValues, setTempSelectedValues] = useState<string[]>(selectedValues);
  const [open, setOpen] = useState(false);
  const { token } = theme.useToken();

  const handleToggleOption = (value: string) => {
    setTempSelectedValues(prev =>
      prev.includes(value)
        ? prev.filter(v => v !== value)
        : [...prev, value]
    );
  };

  const handleClearFilter = (e: React.MouseEvent) => {
    e.stopPropagation();
    setTempSelectedValues([]);
  };

  const handleApplyFilter = () => {
    onChange(tempSelectedValues);
    setOpen(false);
  };

  const handleDropdownVisibleChange = (visible: boolean) => {
    if (visible) {
      setTempSelectedValues(selectedValues);
    }
    setOpen(visible);
  };

  return (
    <Space direction="vertical" style={{ width: '100%' }} size="small">
      <Dropdown
        open={open}
        onOpenChange={handleDropdownVisibleChange}
        popupRender={() => (
          <div style={{
            background: 'white',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            padding: '16px',
          }}>
            <Space direction="vertical" style={{ width: '100%' }} size="middle">
              <Flex justify="space-between" align="center">
                <Text strong>{label}</Text>
                {tempSelectedValues.length > 0 && (
                  <Button
                    size="small"
                    variant="outlined"
                    color="danger"
                    onClick={handleClearFilter}
                    icon={<CloseOutlined />}
                  >
                    Clear all
                  </Button>
                )}
              </Flex>
              <Space style={{ maxWidth: '500px' }} size="small" wrap>
                {isLoading ? (
                  <Spin
                    size="small"
                    style={{
                      width: '200px',
                      textAlign: 'center',
                      padding: '16px 0',
                    }} />
                ) : options.map(option => (
                  <Button
                    key={option.value}
                    style={{
                      cursor: 'pointer',
                      padding: '4px 16px',
                    }}
                    type={tempSelectedValues.includes(option.value) ? 'primary' : 'default'}
                    shape="round"
                    onClick={() => handleToggleOption(option.value)}
                  >
                    {option.label}
                  </Button>
                ))
                }
              </Space>
              <Flex justify="flex-end">
                <Button
                  type="primary"
                  color="purple"
                  variant="solid"
                  icon={<CheckOutlined />}
                  onClick={handleApplyFilter}
                  disabled={isLoading}
                >
                  Apply
                </Button>
              </Flex>
            </Space>
          </div>
        )}
      >
        <Button
          style={{
            borderRadius: '16px',

            ...(selectedValues.length > 0 ? {
              backgroundColor: token.colorInfoBg,
              borderColor: token.colorInfoBorder,
              color: token.colorInfoActive,
            } : {})
          }}
          onClick={(e: MouseEvent) => e.stopPropagation()}
        >
          <Space size="small">
            <Space>
              <span>{label}</span>
              {selectedValues.length > 0 && (
                <span>{`(${selectedValues.length})`}</span>
              )}
            </Space>
            <DownOutlined />
          </Space>
        </Button>
      </Dropdown>

      {selectedValues.length > 0 && (
        <Space wrap>
          {selectedValues.map(value => {
            const option = options.find(opt => opt.value === value);
            return option ? (
              <Tag
                key={value}
                closable
                onClose={() => {
                  const newValues = selectedValues.filter(v => v !== value);
                  onChange(newValues);
                }}
                closeIcon={<CloseOutlined style={{ paddingLeft: 4, color: token.colorTextLightSolid }} />}
                style={{
                  borderRadius: '16px',
                  padding: '4px 16px',
                  backgroundColor: token.colorPrimary,
                  color: token.colorTextLightSolid,
                }}
              >
                {option.label}
              </Tag>
            ) : null;
          })}
        </Space>
      )}
    </Space>
  );
};

export default MultiChoiceFilter;