def two_sum(nums, target):
    """
    给定一个整数数组 nums 和一个整数目标值 target，
    找出数组中和为 target 的两个整数，并返回它们的数组下标。

    Args:
        nums: 整数数组
        target: 目标值

    Returns:
        包含两个整数下标的列表，如果没有找到则返回空列表
    """
    # 使用哈希表存储已遍历过的数字及其索引
    num_map = {}

    for i, num in enumerate(nums):
        # 计算当前数字需要配对的数字
        complement = target - num

        # 如果配对数字已在哈希表中，则找到了答案
        if complement in num_map:
            return [num_map[complement], i]

        # 将当前数字和其索引存入哈希表
        num_map[num] = i

    # 如果没有找到符合条件的两个数，返回空列表
    return []


# 测试用例
if __name__ == "__main__":
    # 示例1
    nums1 = [2, 7, 11, 15]
    target1 = 9
    result1 = two_sum(nums1, target1)
    print(f"输入: nums = {nums1}, target = {target1}")
    print(f"输出: {result1}")
    print(f"解释: {nums1[result1[0]]} + {nums1[result1[1]]} = {target1}\n")

    # 示例2
    nums2 = [3, 2, 4]
    target2 = 6
    result2 = two_sum(nums2, target2)
    print(f"输入: nums = {nums2}, target = {target2}")
    print(f"输出: {result2}")
    print(f"解释: {nums2[result2[0]]} + {nums2[result2[1]]} = {target2}\n")

    # 示例3
    nums3 = [3, 3]
    target3 = 6
    result3 = two_sum(nums3, target3)
    print(f"输入: nums = {nums3}, target = {target3}")
    print(f"输出: {result3}")
    print(f"解释: {nums3[result3[0]]} + {nums3[result3[1]]} = {target3}\n")