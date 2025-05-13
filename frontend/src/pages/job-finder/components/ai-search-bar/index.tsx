import { Flex } from "antd";

import { Input } from "antd";
import { SearchOutlined } from "@ant-design/icons";

import { motion } from "framer-motion";
import { ChangeEvent, KeyboardEvent } from "react";

import AIButton from "../../../../components/ai-button";
import { Stars } from "react-bootstrap-icons";
import { purple } from "@ant-design/colors";

interface AISearchBarProps {
  searchValue: string;
  setSearchValue: (value: string) => void;
  handleSearch: (value: string) => void;
}

const AISearchBar = ({ searchValue, setSearchValue, handleSearch }: AISearchBarProps) => {
  return (
    <Flex
      align="center"
      justify="center"
      style={{
        width: "100%",
        maxWidth: "700px",
        margin: "24px 0 16px"
      }}
      gap="small"
    >
      <div style={{
        display: "flex",
        width: "100%",
        position: "relative",
        alignItems: "center",
        backgroundColor: "#fff",
        borderRadius: 32,
        padding: "4px 16px",
        background:
          "linear-gradient(white, white) padding-box, linear-gradient(180deg, #1677FF 0%, #5466EF 50%, #9254DE 100%) border-box",
        border: "1px solid transparent",
      }}>
        <motion.div
          animate="animate"
          variants={{
            animate: {
              rotate: [0, 15, -15, 0],
              scale: [1, 1.3, 1],
              transition: {
                duration: 2,
                repeat: Infinity,
                repeatType: "loop" as const,
                ease: "easeInOut"
              }
            }
          }}
        >
          <Stars
            style={{
              color: purple[5],
              fontSize: 16,
            }}
          />
        </motion.div>
        <Input.TextArea
          placeholder="I am looking for..."
          allowClear
          variant="borderless"
          size="large"
          value={searchValue}
          onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setSearchValue(e.target.value)}
          onPressEnter={(e: KeyboardEvent<HTMLTextAreaElement>) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSearch(searchValue);
            }
          }}
          style={{
            overflow: "auto",
          }}
          autoSize={{ minRows: 1, maxRows: 4 }}
        />
      </div>
      <AIButton
        shape="circle"
        size="large"
        onClick={() => handleSearch(searchValue)}
      >
        <SearchOutlined style={{ color: "#fff", padding: 8 }} />
      </AIButton>
    </Flex>
  )
};

export default AISearchBar;