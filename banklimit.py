# IN PROGRESS IN PROGRESS IN PROGRESS
#
#

import csv
import json
import datetime
from pathlib import Path
from abc import ABC, abstractmethod

now = datetime.datetime.now()
change_count = 0
STATE_FILE = Path(__file__).with_name("budget_state.json")
print(f"Program started at: {now:%Y-%m-%d %H:%M:%S}")


class Info(ABC):
    @abstractmethod
    def summary(self):
        """Return a readable summary string for this budget item."""
        raise NotImplementedError

    @abstractmethod
    def export_row(self):
        """Return a row that can be saved to CSV."""
        raise NotImplementedError


class BudgetInfo(Info):
    def __init__(self, category, limit, subcategory="", sub_limit=0.0):
        self.category = category
        self.limit = float(limit)
        self.subcategory = subcategory
        self.sub_limit = float(sub_limit)

    def summary(self):
        if self.subcategory:
            return (
                f"{self.category} / {self.subcategory}: "
                f"${self.sub_limit:.2f} of ${self.limit:.2f}"
            )
        return f"{self.category}: ${self.limit:.2f}"

    def export_row(self):
        return [
            self.category,
            self.limit,
            self.subcategory,
            self.sub_limit,
        ]

    def __str__(self):
        return self.summary()


class BankLimit:
    def __init__(self):
        self.categories = {}
        self.locked = False
        self.change_count = 0
        self.max_changes = 5
        self.yearly_salary = 0
        self.monthly_salary = 0
        self.weekly_salary = 0
        self.bi_weekly_salary = 0
        self.salary_type = None
        self.last_reset_month = None
        self.state_file = STATE_FILE
        self.load_state()
        self._reset_monthly_limits_if_needed()

    def _current_month_key(self):
        now = datetime.datetime.now()
        return f"{now.year}-{now.month:02d}"

    def _reset_monthly_limits_if_needed(self):
        current_month = self._current_month_key()
        if self.last_reset_month != current_month:
            self.change_count = 0
            self.locked = False
            self.last_reset_month = current_month
            self.save_state()

    def load_state(self):
        if not self.state_file.exists():
            self.last_reset_month = self._current_month_key()
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            print("No saved budget state found or the saved data is invalid.")
            self.last_reset_month = self._current_month_key()
            return

        self.categories = data.get("categories", {})
        self.locked = bool(data.get("locked", False))
        self.change_count = int(data.get("change_count", 0))
        self.max_changes = int(data.get("max_changes", self.max_changes))
        self.yearly_salary = float(data.get("yearly_salary", 0))
        self.monthly_salary = float(data.get("monthly_salary", 0))
        self.weekly_salary = float(data.get("weekly_salary", 0))
        self.bi_weekly_salary = float(data.get("bi_weekly_salary", 0))
        self.salary_type = data.get("salary_type")
        self.last_reset_month = data.get("last_reset_month")

        if self.categories:
            print("Saved budget state loaded.")

    def save_state(self):
        state = {
            "categories": self.categories,
            "locked": self.locked,
            "change_count": self.change_count,
            "max_changes": self.max_changes,
            "yearly_salary": self.yearly_salary,
            "monthly_salary": self.monthly_salary,
            "weekly_salary": self.weekly_salary,
            "bi_weekly_salary": self.bi_weekly_salary,
            "salary_type": self.salary_type,
            "last_reset_month": self.last_reset_month,
        }

        with self.state_file.open("w", encoding="utf-8") as file:
            json.dump(state, file, indent=2)

    def _total_allocated(self):
        return sum(
            info["limit"] for info in self.categories.values()
        )

    def menu(self):
        while True:
            self._reset_monthly_limits_if_needed()
            print("\nMenu:")
            print("1. Add Category")
            print("2. Show Categories")
            print("3. Delete category/subcategory")
            print("4. Preset Categories (50/30/20 Rule)")
            print("5. Change Limit")
            print("6. Show Limit Change")
            print("7. View Total Budget")
            print("8. Save Budget to CSV")
            print("9. View Percentage Shares")
            print("10. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_category()
            elif choice == "2":
                self.show_categories()
            elif choice == "3":
                self.delete_category_or_subcategory()
            elif choice == "4":
                self.preset_categories()
            elif choice == "5":
                self.change_limit()
            elif choice == "6":
                self.show_limit()
            elif choice == "7":
                self.view_total_budget()
            elif choice == "8":
                self.save_to_csv()
            elif choice == "9":
                self.percentage_shares()
            elif choice == "10":
                self.save_state()
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def _prompt_percentage(self, label):
        while True:
            try:
                percentage = float(
                    input(f"Enter the {label} percentage (0-100): ")
                )
            except ValueError:
                print("The percentage must be a number.")
                continue

            if percentage < 0 or percentage > 100:
                print("The percentage must be between 0 and 100.")
                continue

            return percentage

    def add_category(self):
        category = input("Enter the category: ").title()

        if category in self.categories:
            print("Category already exists.")
            return

        percentage = None
        limit = None

        if self.monthly_salary > 0:
            while True:
                choice = input(
                    "Would you like to add a percentage target for "
                    "this category? (yes/no/number): "
                ).lower()

                if choice == "yes":
                    percentage = self._prompt_percentage("category")
                    limit = self.monthly_salary * (percentage / 100)
                    print(
                        f"Using {percentage:.2f}% of your monthly salary "
                        f"for '{category}', which equals ${limit:.2f}."
                    )
                    break
                elif choice == "number":
                    break
                elif choice == "no":
                    break
                else:
                    print("Please enter 'yes', 'no', or 'number'.")

        if limit is None and self.monthly_salary > 0:
            if choice == "number":
                try:
                    limit = float(input("Enter the limit: "))
                except ValueError:
                    print("The limit must be a number.")
                    return
            elif choice == "no":
                try:
                    limit = float(input("Enter the limit: "))
                except ValueError:
                    print("The limit must be a number.")
                    return

        if limit is None:
            try:
                limit = float(input("Enter the limit: "))
            except ValueError:
                print("The limit must be a number.")
                return

        if limit < 0:
            print("Limit cannot be negative.")
            return

        total_after_add = self._total_allocated() + limit
        if self.monthly_salary > 0 and total_after_add > self.monthly_salary:
            print(
                f"Cannot add ${limit:.2f} to '{category}'. "
                f"Your total budget would be ${total_after_add:.2f}, "
                f"which exceeds your monthly income of "
                f"${self.monthly_salary:.2f}."
            )
            return

        self.categories[category] = {
            "limit": limit,
            "percentage": percentage,
            "subcategories": {},
            "subcategory_percentages": {},
        }
        self.save_state()

        print(f"Category '{category}' added with limit ${limit:.2f}.")
        if percentage is not None:
            print(f"Category percentage target: {percentage:.2f}%.")

        choice = input(
            "Would you like to add subcategories? (yes/no): "
        ).lower()

        if choice == "yes":
            self.add_subcategories(category)

    def add_subcategories(self, category):
        while True:
            subcategory = input(
                f"Enter a subcategory for {category} "
                "(or type 'done' to finish): "
            ).title()

            if subcategory.lower() == "done":
                break

            if subcategory in self.categories[category]["subcategories"]:
                print("Subcategory already exists.")
                continue

            percentage = None
            use_percentage = input(
                f"Would you like to set a percentage target for "
                f"'{subcategory}'? (yes/no): "
            ).lower()

            if use_percentage == "yes":
                percentage = self._prompt_percentage("subcategory")

            try:
                if percentage is not None:
                    category_limit = self.categories[category]["limit"]
                    limit = category_limit * (percentage / 100)
                else:
                    limit = float(
                        input(f"Enter the limit for {subcategory}: ")
                    )
            except ValueError:
                print("The limit must be a number.")
                continue
            except KeyboardInterrupt:
                print("\nOperation cancelled.")
                break

            if limit < 0:
                print("Limit cannot be negative.")
                continue

            used = sum(
                self.categories[category]["subcategories"].values()
            )

            category_limit = self.categories[category]["limit"]
            remaining = category_limit - used

            if limit > remaining:
                print(
                    f"Cannot add ${limit:.2f}. "
                    f"{category} only has ${remaining:.2f} remaining."
                )
                continue

            self.categories[category]["subcategories"][subcategory] = limit
            if percentage is not None:
                self.categories[category]["subcategory_percentages"][
                    subcategory
                ] = percentage

            self.save_state()
            print(
                f"Subcategory '{subcategory}' added under '{category}'."
            )
            if percentage is not None:
                print(f"Subcategory percentage target: {percentage:.2f}%.")

    def show_categories(self):
        if not self.categories:
            print("No categories have been added.")
            return

        for category, info in self.categories.items():
            print(f"\n{category}: ${info['limit']:.2f}")
            if info.get("percentage") is not None:
                print(f"  Percentage target: {info['percentage']:.2f}%")

            subcategories = info["subcategories"]

            if subcategories:
                used = 0

                for subcategory, limit in subcategories.items():
                    percentage = info.get(
                        "subcategory_percentages", {}
                    ).get(subcategory)
                    if percentage is not None:
                        print(
                            f"  - {subcategory}: ${limit:.2f} "
                            f"({percentage:.2f}%)"
                        )
                    else:
                        print(f"  - {subcategory}: ${limit:.2f}")
                    used += limit

                remaining = info["limit"] - used

                print(f"  Used: ${used:.2f}")
                print(f"  Remaining in {category}: ${remaining:.2f}")

    def view_total_budget(self):
        if self.monthly_salary <= 0:
            print("No salary has been entered yet.")
            return

        allocated = sum(
            info["limit"]
            for info in self.categories.values()
        )

        remaining = self.monthly_salary - allocated

        print(f"Monthly Income: ${self.monthly_salary:.2f}")
        print(f"Allocated Budget: ${allocated:.2f}")
        print(f"Remaining Budget: ${remaining:.2f}")

    def preset_categories(self):
        try:
            salary_type = input(
                "What is the frequency of your salary? "
                "(yearly/monthly/bi-weekly/weekly): "
            ).lower()

            if salary_type == "yearly":
                yearly_salary = float(
                    input("Enter your yearly income/salary: ")
                )
                if yearly_salary <= 0:
                    print("Salary must be greater than zero.")
                    return

                self.yearly_salary = yearly_salary
                self.monthly_salary = yearly_salary / 12
                self.bi_weekly_salary = yearly_salary / 26
                self.weekly_salary = yearly_salary / 52

            elif salary_type == "monthly":
                monthly_salary = float(
                    input("Enter your monthly income/salary: ")
                )
                if monthly_salary <= 0:
                    print("Salary must be greater than zero.")
                    return

                self.monthly_salary = monthly_salary
                self.yearly_salary = monthly_salary * 12
                self.bi_weekly_salary = monthly_salary * 12 / 26
                self.weekly_salary = monthly_salary * 12 / 52

            elif salary_type == "bi-weekly":
                bi_weekly_salary = float(
                    input("Enter your bi-weekly income/salary: ")
                )
                if bi_weekly_salary <= 0:
                    print("Salary must be greater than zero.")
                    return

                self.bi_weekly_salary = bi_weekly_salary
                self.weekly_salary = bi_weekly_salary / 2
                self.yearly_salary = bi_weekly_salary * 26
                self.monthly_salary = self.yearly_salary / 12

            elif salary_type == "weekly":
                weekly_salary = float(
                    input("Enter your weekly income/salary: ")
                )
                if weekly_salary <= 0:
                    print("Salary must be greater than zero.")
                    return

                self.weekly_salary = weekly_salary
                self.bi_weekly_salary = weekly_salary * 2
                self.yearly_salary = weekly_salary * 52
                self.monthly_salary = self.yearly_salary / 12

            else:
                print("Invalid salary frequency.")
                return

        except ValueError:
            print("Salary must be a number.")
            return

        self.salary_type = salary_type
        self.categories["Needs"] = {
            "limit": self.monthly_salary * 0.50,
            "percentage": 50.0,
            "subcategories": {},
            "subcategory_percentages": {},
        }
        self.categories["Wants"] = {
            "limit": self.monthly_salary * 0.30,
            "percentage": 30.0,
            "subcategories": {},
            "subcategory_percentages": {},
        }
        self.categories["Savings"] = {
            "limit": self.monthly_salary * 0.20,
            "percentage": 20.0,
            "subcategories": {},
            "subcategory_percentages": {},
        }

        self.save_state()
        print("50/30/20 preset added.")

        self.show_categories()

        choice = input(
            "\nWould you like to add subcategories "
            "to the preset categories? (yes/no): "
        ).lower()

        if choice == "yes":
            for category in ["Needs", "Wants", "Savings"]:
                add_sub = input(
                    f"Add subcategories to {category}? (yes/no): "
                ).lower()

                if add_sub == "yes":
                    self.add_subcategories(category)

    def delete_category_or_subcategory(self):
        if not self.categories:
            print("No categories have been added.")
            return

        category = input("Enter the category name: ").title()
        if category not in self.categories:
            print("Category does not exist.")
            return

        subcategory = input(
            "Enter a subcategory to delete "
            f"(or press Enter to delete {category}): "
        ).title()

        if (
            subcategory
            and subcategory in self.categories[category]["subcategories"]
        ):
            del self.categories[category]["subcategories"][subcategory]
            self.categories[category]["subcategory_percentages"].pop(
                subcategory,
                None,
            )
            self.save_state()
            print(f"Subcategory '{subcategory}' removed from '{category}'.")
            return

        if subcategory:
            print("Subcategory does not exist.")
            return

        del self.categories[category]
        self.save_state()
        print(f"Category '{category}' removed.")

    def subcategory_list(self, category):
        if category not in self.categories:
            print("Category does not exist.")
            return

        subcategories = self.categories[category]["subcategories"]

        if not subcategories:
            print(f"No subcategories for {category}.")
            return

        print(f"Subcategories for {category}:")
        for subcategory, limit in subcategories.items():
            print(f"  - {subcategory}: ${limit:.2f}")

    def show_limit(self):
        changes_left = self.max_changes - self.change_count
        print(f"You have {changes_left} changes left")

    def change_limit(self):
        if self.locked:
            print("Your budget is locked for this month.")
            return

        if self.change_count >= self.max_changes:
            self.locked = True
            print("You have reached the maximum number of changes.")
            return

        category = input(
            "Enter the category whose limit you want to change: "
        ).title()

        if category not in self.categories:
            print("Category does not exist.")
            return

        try:
            new_limit = float(input("Enter the new limit: "))
        except ValueError:
            print("The limit must be a number.")
            return

        if new_limit < 0:
            print("Limit cannot be negative.")
            return

        subcategory_total = sum(
            self.categories[category]["subcategories"].values()
        )

        if new_limit < subcategory_total:
            print(
                f"Cannot lower {category} to ${new_limit:.2f}."
            )
            print(
                f"Its subcategories already total "
                f"${subcategory_total:.2f}."
            )
            return

        old_limit = self.categories[category]["limit"]
        new_total = self._total_allocated() - old_limit + new_limit

        if self.monthly_salary > 0 and new_total > self.monthly_salary:
            print(
                f"Cannot change '{category}' to ${new_limit:.2f}. "
                f"That would raise your total budget to "
                f"${new_total:.2f}, which exceeds your monthly income of "
                f"${self.monthly_salary:.2f}."
            )
            return

        self.categories[category]["limit"] = new_limit
        self.change_count += 1
        self._reset_monthly_limits_if_needed()
        self.save_state()

        changes_left = self.max_changes - self.change_count

        print(
            f"{category} changed from "
            f"${old_limit:.2f} to ${new_limit:.2f}."
        )
        print(
            f"Changes used: "
            f"{self.change_count}/{self.max_changes}."
        )
        print(f"Changes remaining: {changes_left}.")

        if self.change_count >= self.max_changes:
            self.locked = True
            print("Your budget is now locked for this month.")

    def percentage_shares(self):
        if not self.categories:
            print("No categories have been added.")
            return

        if self.monthly_salary <= 0:
            print("No salary has been entered yet.")
            return

        print("\nBudget percentage shares:")
        for category, info in self.categories.items():
            category_percentage = (info["limit"] / self.monthly_salary) * 100
            print(
                f"- {category}: {category_percentage:.2f}% of monthly "
                f"income (${info['limit']:.2f} / ${self.monthly_salary:.2f})"
            )

            for subcategory, sub_limit in info["subcategories"].items():
                if info["limit"] > 0:
                    sub_percentage = (sub_limit / info["limit"]) * 100
                else:
                    sub_percentage = 0
                print(
                    f"  - {subcategory}: {sub_percentage:.2f}% of "
                    f"{category}"
                )

        detail_choice = input(
            "Would you like to view a specific category in detail? (yes/no): "
        ).lower()

        if detail_choice != "yes":
            return

        category = input("Enter the category name: ").title()
        if category not in self.categories:
            print("Category does not exist.")
            return

        info = self.categories[category]
        category_percentage = (info["limit"] / self.monthly_salary) * 100
        print(
            f"{category} uses {category_percentage:.2f}% of your monthly "
            f"income (${info['limit']:.2f} / ${self.monthly_salary:.2f})."
        )

        if not info["subcategories"]:
            print(f"{category} has no subcategories.")
            return

        for subcategory, sub_limit in info["subcategories"].items():
            if info["limit"] > 0:
                sub_percentage = (sub_limit / info["limit"]) * 100
            else:
                sub_percentage = 0
            print(
                f"- {subcategory}: {sub_percentage:.2f}% of {category} "
                f"(${sub_limit:.2f})"
            )

    def save_to_csv(self, filename="budget.csv"):
        try:
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)

                writer.writerow(
                    [
                        "Category",
                        "Category Limit",
                        "Category Percentage",
                        "Subcategory",
                        "Subcategory Limit",
                        "Subcategory Percentage",
                    ]
                )

                for category, info in self.categories.items():
                    subcategories = info["subcategories"]

                    if not subcategories:
                        row = [
                            category,
                            info["limit"],
                            info.get("percentage", ""),
                            "",
                            "",
                            "",
                        ]
                        writer.writerow(row)
                    else:
                        for subcategory, sub_limit in subcategories.items():
                            row = [
                                category,
                                info["limit"],
                                info.get("percentage", ""),
                                subcategory,
                                sub_limit,
                                info.get(
                                    "subcategory_percentages",
                                    {},
                                ).get(subcategory, ""),
                            ]
                            writer.writerow(row)

            print(f"Budget saved to {filename}")

        except Exception as e:
            print(f"Error saving file: {e}")


bank = BankLimit()
bank.menu()

