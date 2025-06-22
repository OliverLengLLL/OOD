from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

class Promotion(ABC):
    @abstractmethod
    def getFinalPrice(self, totalPrice):
        pass

class EightPercentPromotion(Promotion):
    def getFinalPrice(self, totalPrice):
        if totalPrice > 100:
            return totalPrice * 0.92
        return totalPrice

class TenPercentPromotion(Promotion):
    def getFinalPrice(self, totalPrice):
        if totalPrice > 50:
            return totalPrice * 0.90
        return totalPrice

class Pizza(ABC):
    def __init__(self, name: str, size: str, price: float):
        self.name = name
        self.size = size  # small, medium, large
        self.price = price

    def __str__(self):
        return f"{self.size.capitalize()} {self.name} Pizza: ${self.price:.2f}"

    @abstractmethod
    def getSmallSizePrice(self, size, promotion: Promotion) -> float:
        pass

    @abstractmethod
    def getMediumSizePrice(self, size, promotion: Promotion) -> float:
        pass

    @abstractmethod
    def getLargeSizePrice(self, size, promotion: Promotion) -> float:
        pass

class BasicPizza(Pizza):
    def getSmallSizePrice(self, size, promotion: Promotion) -> float:
        return promotion.getFinalPrice(10.0)

    def getMediumSizePrice(self, size, promotion: Promotion) -> float:
        return promotion.getFinalPrice(15.0)
 
    def getLargeSizePrice(self, size, promotion: Promotion) -> float:
        return promotion.getFinalPrice(20.0)
    
class PizzaDecorator(Pizza):
    def __init__(self, pizza: Pizza):
        self._pizza = pizza
        super().__init__(pizza.name, pizza.size, pizza.price)

    def getSmallSizePrice(self, size, promotion: Promotion) -> float:
        return self._pizza.getSmallSizePrice(size, promotion)

    def getMediumSizePrice(self, size, promotion: Promotion) -> float:
        return self._pizza.getMediumSizePrice(size, promotion)

    def getLargeSizePrice(self, size, promotion: Promotion) -> float:
        return self._pizza.getLargeSizePrice(size, promotion)
    
class ExtraCheeseDecorator(PizzaDecorator):
    def __init__(self, pizza: Pizza):
        super().__init__(pizza)
        self.name = f"{pizza.name} with Extra Cheese"
    def getSmallSizePrice(self, size, promotion: Promotion) -> float:
        return super().getSmallSizePrice(size, promotion) + 2.0

    def getMediumSizePrice(self, size, promotion: Promotion) -> float:
        return super().getMediumSizePrice(size, promotion) + 3.0

    def getLargeSizePrice(self, size, promotion: Promotion) -> float:
        return super().getLargeSizePrice(size, promotion) + 4.0


def main():
    promotion = EightPercentPromotion()
    
    # Create a basic pizza
    basic_pizza = BasicPizza("Margherita", "medium", 15.0)
    print(basic_pizza)

    basic_pizza = ExtraCheeseDecorator(basic_pizza)
    basic_pizza = ExtraCheeseDecorator(basic_pizza)
    print(basic_pizza)
    print(f"Small Size Price: ${basic_pizza.getSmallSizePrice('small', promotion):.2f}")
    print(f"Medium Size Price: ${basic_pizza.getMediumSizePrice('medium', promotion):.2f}")
    print(f"Large Size Price: ${basic_pizza.getLargeSizePrice('large', promotion):.2f}")
if __name__ == "__main__":
    main()


class Solution:
    def findMatchingAds(self, orders: List[Tuple[int, str]], ads: List[Tuple[int, str]]) -> List[Optional[Tuple[int, str]]]:
        j = 0
        last_ad = {}
        result = []

        for time_order, product_id in orders:
            while j < len(ads) and ads[j][0] < time_order:
                time_ad, pid_ad = ads[j]
                last_ad[pid_ad] = time_ad
                j += 1

            if product_id  in last_ad:
                result.append((last_ad[product_id], product_id))
            
        return result
    
class TreeNode:
    def __init__(self, value: str):
        self.value = value
        self.children: List['TreeNode'] = []

    def addChild(self, child: 'TreeNode') -> None:
        self.children.append(child)

class Employee:
    def __init__(self, name):
        self.name = name
        self.reports = []

class Solution2:

    def compress_nodes(self, root, compressedNodes):
        compressedNodes = set(compressedNodes)

        def traverse(node):
            if not node:
                return

            for child in node.children:
                traverse(child)

            new_children = []
            for child in node.children:
                if child.val in compressedNodes:
                    new_children.extend(child.children)
                else:
                    new_children.append(child)

            node.children = new_children
        
        traverse(root)
        return root
    
    def lowest_common_manager(self, root, emp1, emp2):
        def traverse(root):
            if not root:
                return None
            
            if root == emp1 or root == emp2:
                return root
            
            results = []
            for report in root.reports:
                child_results = traverse(report)
                if child_results:
                    results.append(child_results)

            if len(results) > 1:
                return root
            
            result = results[0] if results else None
            return result

        return traverse(root)
    


class MeetingScheduler:
    def __init__(self, roomList: List[str]):
        # Used as a TreeMap to ensure rooms are sorted by alphabetical order
        self.recordMap = {}
        for room in roomList:
            self.recordMap[room] = []

    def schedule(self, start: int, end: int) -> str:
        # Check each room in alphabetical order
        for room in sorted(self.recordMap.keys()):
            times = self.recordMap[room]

            # Use binary search to find the correct insertion point
            insertPos = self.findInsertPosition(times, start, end)

            # Check if there is a conflict with the interval at insertPos-1
            if insertPos > 0:
                prevInterval = times[insertPos - 1]
                if prevInterval[1] > start:
                    # conflict
                    continue

            # Check if there is a conflict with the interval at insertPos
            if insertPos < len(times):
                nextInterval = times[insertPos]
                if nextInterval[0] < end:
                    # conflict
                    continue

            # If no conflict, insert the new interval and return
            times.insert(insertPos, [start, end])
            return room

        return ""  # No room is available

    def findInsertPosition(self, intervals: List[List[int]], start: int, end: int) -> int:
        low = 0
        high = len(intervals) - 1

        while low <= high:
            mid = (low + high) // 2
            current = intervals[mid]

            # If the current interval starts after 'end', search left
            if current[0] >= end:
                high = mid - 1
            # If the current interval ends before 'start', search right
            elif current[1] <= start:
                low = mid + 1
            else:
                high = mid - 1
        return low

    def loadTruck(self, trucks: List[int], items: List[int]) -> List[int]:
        sorted_trucks = sorted([(cap, idx) for idx, cap in enumerate(trucks)])

        res = []
        for w in items:
            l, r = 0, len(sorted_trucks) - 1
            while l <= r:
                mid = (l + r) // 2
                if sorted_trucks[mid][0] <= w:        # capacity too small → go right
                    l = mid + 1
                else:                                 # capacity large enough → go left
                    r = mid - 1

            # l now points at the first truck whose capacity > w
            if l < len(sorted_trucks):
                res.append(sorted_trucks[l][1])       # original index lives in the tuple
            else:
                res.append(-1)                        # no truck fits

            return res
        
    def findIndexEqualNumber(self, nums: List[int]) -> int:
        l, r = 0, len(nums) - 1

        while l <= r:
            mid = (l + r) // 2

            if nums[mid] == mid:
                return mid
            elif nums[mid] < mid:
                l = mid+1
            else:
                r = mid-1

        return -1