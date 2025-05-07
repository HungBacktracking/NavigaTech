import { useEffect } from "react";
import { motion, stagger, useAnimate, useInView } from "framer-motion";

export const TypewriterEffect = ({
  words,
  className,
  cursorClassName,
}: {
  words: {
    text: string;
    className?: string;
  }[];
  className?: string;
  cursorClassName?: string;
}) => {
  const wordsArray = words.map((word) => {
    return {
      ...word,
      text: word.text.split(""),
    };
  });

  const [scope, animate] = useAnimate();
  const isInView = useInView(scope);

  useEffect(() => {
    if (isInView) {
      animate(
        "span",
        {
          display: "inline-block",
          opacity: 1,
          width: "fit-content",
        },
        {
          duration: 0.3,
          delay: stagger(0.1),
          ease: "easeInOut",
        }
      );
    }
  }, [isInView, animate]);

  const renderWords = () => {
    return (
      <motion.div ref={scope} style={{ display: "inline" }}>
        {wordsArray.map((word, idx) => {
          return (
            <div key={`word-${idx}`} style={{ display: "inline-block" }}>
              {word.text.map((char, index) => (
                <motion.span
                  initial={{}}
                  key={`char-${index}`}
                  className={word.className}
                  style={{
                    color: "inherit",
                    opacity: 0,
                    display: "none",
                  }}
                >
                  {char}
                </motion.span>
              ))}
              &nbsp;
            </div>
          );
        })}
      </motion.div>
    );
  };

  return (
    <div
      className={className}
      style={{
        fontSize: "1.25rem",
        fontWeight: "bold",
        textAlign: "center",
        ...(!className && {
          fontSize: "clamp(1rem, 5vw, 3rem)",
          fontWeight: "bold",
          textAlign: "center",
        }),
      }}
    >
      {renderWords()}
      <motion.span
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          repeatType: "reverse",
        }}
        className={cursorClassName}
        style={{
          display: "inline-block",
          borderRadius: "2px",
          width: "4px",
          height: cursorClassName ? undefined : "clamp(1rem, 5vw, 2.5rem)",
          backgroundColor: "#1890ff",
          ...(!cursorClassName && {
            verticalAlign: "middle",
          }),
        }}
      ></motion.span>
    </div>
  );
};

export const TypewriterEffectSmooth = ({
  words,
  className,
  cursorClassName,
}: {
  words: {
    text: string;
    className?: string;
  }[];
  className?: string;
  cursorClassName?: string;
}) => {
  // Split text inside of words into array of characters
  const wordsArray = words.map((word) => {
    return {
      ...word,
      text: word.text.split(""),
    };
  });

  const renderWords = () => {
    return (
      <div>
        {wordsArray.map((word, idx) => {
          return (
            <div key={`word-${idx}`} style={{ display: "inline-block" }}>
              {word.text.map((char, index) => (
                <span
                  key={`char-${index}`}
                  className={word.className}
                  style={{
                    color: "inherit",
                  }}
                >
                  {char}
                </span>
              ))}
              &nbsp;
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div
      className={className}
      style={{
        display: "flex",
        marginTop: "1.5rem",
        marginBottom: "1.5rem",
        ...(!className && {
          display: "flex",
          marginTop: "1.5rem",
          marginBottom: "1.5rem",
        }),
      }}
    >
      <motion.div
        style={{
          overflow: "hidden",
          paddingBottom: "0.5rem",
        }}
        initial={{
          width: "0%",
        }}
        whileInView={{
          width: "fit-content",
        }}
        transition={{
          duration: 2,
          ease: "linear",
          delay: 1,
        }}
      >
        <div
          style={{
            whiteSpace: "nowrap",
            fontSize: "clamp(0.875rem, 5vw, 3rem)",
            fontWeight: "bold",
          }}
        >
          {renderWords()}{" "}
        </div>{" "}
      </motion.div>
      <motion.span
        initial={{
          opacity: 0,
        }}
        animate={{
          opacity: 1,
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          repeatType: "reverse",
        }}
        className={cursorClassName}
        style={{
          display: "block",
          borderRadius: "2px",
          width: "4px",
          height: cursorClassName ? undefined : "clamp(1rem, 5vw, 3rem)",
          backgroundColor: "#1890ff",
        }}
      ></motion.span>
    </div>
  );
};