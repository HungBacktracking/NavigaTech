import { Button, Image, Space } from "antd";
import error404Svg from "../../assets/error-404.svg";

const NotFoundPage = () => {
  return (
    <Space direction="vertical" style={{ width: '100%', textAlign: 'center' }} align="center">
      <Image
        src={error404Svg}
        preview={false}
        style={{ width: 600, objectFit: 'cover' }}
        alt="404 Not Found"
      />
      <Button
        type="primary"
        onClick={() => window.location.href = '/home'}
      >
        Go to Home
      </Button>
    </Space>
  )
};

export default NotFoundPage;