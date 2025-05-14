export const extractDomainFromUrl = (url: string) => {
  try {
    const domain = new URL(url).hostname.replace('www.', '');
    return domain;
  } catch (e) {
    return url;
  }
};

export const formatDateToEngPeriodString = (date: string | undefined) => {
  if (!date) return "";
  const parsedDate = new Date(date);
  const now = new Date();
  const diffTime = Math.abs(now.getTime() - parsedDate.getTime());
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    const hours = parsedDate.getHours();
    const minutes = parsedDate.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const formattedHours = hours % 12 || 12;
    const formattedMinutes = minutes < 10 ? `0${minutes}` : minutes;
    return `${formattedHours}:${formattedMinutes} ${ampm} Today`;
  }
  if (diffDays === 1) return "Yesterday";
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return `${Math.floor(diffDays / 30)} months ago`;
};
