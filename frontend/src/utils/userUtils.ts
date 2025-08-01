/**
 * 用户ID处理工具函数
 */

/**
 * 将用户ID转换为base64编码的显示ID（取前8位）
 * @param userId - 原始用户ID
 * @returns base64编码的前8位字符串
 */
export const getUserDisplayId = (userId: number | string): string => {
  if (!userId) return '00000000';
  
  // 将用户ID转换为字符串，并添加一些盐值以增加复杂度
  const saltedId = `user_${userId}_${new Date().getFullYear()}`;
  
  // 转换为base64
  const base64Id = btoa(saltedId);
  
  // 取前8位
  return base64Id.substring(0, 8).toUpperCase();
};

/**
 * 生成用户显示ID的另一种方案（基于时间戳和用户ID）
 * @param userId - 原始用户ID
 * @returns 8位显示ID
 */
export const getUserDisplayIdV2 = (userId: number | string): string => {
  if (!userId) return '00000000';
  
  // 使用用户ID和固定盐值生成更稳定的显示ID
  const stableString = `offerotter_${userId}_2025`;
  const base64Id = btoa(stableString);
  
  // 确保总是8位，不足的用0补齐
  const displayId = base64Id.substring(0, 8).toUpperCase();
  return displayId.padEnd(8, '0');
};

/**
 * 格式化显示用户ID（添加前缀）
 * @param userId - 原始用户ID
 * @returns 格式化的显示ID，如 "ID:AB12CD34"
 */
export const formatUserDisplayId = (userId: number | string): string => {
  const displayId = getUserDisplayIdV2(userId);
  return `ID:${displayId}`;
}; 