import csv
import datetime

now = datetime.datetime.now()
print(f"Program started at: {now:%Y-%m-%d %H:%M:%S}")


class BankLimit:
    def __init__(self):
        self.categories = {}
        self.locked = False
        self.change_count = 0
        self.max_changes = 5
        self.yearly_salary = 0
        self.monthly_salary = 0

    def menu(self):
        while True:
            print("\nMenu:")
            print("1. Add Category")
            print("2. Show Categories")
            print("3. Remove Category")
            print("4. Preset Categories (50/30/20 Rule)")
            print("5. Change Limit")
            print("6. View Total Budget")
            print("7. Save Budget to CSV")
            print("8. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                self.add_category()
            elif choice == "2":
                self.show_categories()
            elif choice == "3":
                self.remove_category()
            elif choice == "4":
                self.preset_categories()
            elif choice == "5":
                self.change_limit()
            elif choice == "6":
                self.view_total_budget()
            elif choice == "7":
                self.save_to_csv()
            elif choice == "8":
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    #implement the add_category method
    def add_category(self):
        category = input("Enter the category: ").title()

        if category in self.categories:
            print("Category already exists.")
            return

        try:
            limit = float(input("Enter the limit: "))
        except ValueError:
            print("The limit must be a number.")
            return

        if limit < 0:
            print("Limit cannot be negative.")
            return

        if limit > self.monthly_salary:
            print(
                f"Cannot add ${limit:.2f}. "
                f"Your monthly salary is only ${self.monthly_salary:.2f}."
            )
            return
        #subcategories inside the category dictionary
        self.categories[category] = {
            "limit": limit,
            "subcategories": {}
        }

        print(f"Category '{category}' added with limit ${limit:.2f}.")

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

            try:
                limit = float(
                    input(f"Enter the limit for {subcategory}: ")
                )
            except ValueError:
                print("The limit must be a number.")
                continue

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

            print(
                f"Subcategory '{subcategory}' added under '{category}'."
            )

    def show_categories(self):
        if not self.categories:
            print("No categories have been added.")
            return

        for category, info in self.categories.items():
            print(f"\n{category}: ${info['limit']:.2f}")

            subcategories = info["subcategories"]

            if subcategories:
                used = 0

                for subcategory, limit in subcategories.items():
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

    def remove_category(self):
        if not self.categories:
            print("No categories have been added.")
            return

        print("Current Categories:")

        for category, info in self.categories.items():
            print(f"{category}: ${info['limit']:.2f}")

        category = input(
            "Enter the category to remove: "
        ).title()

        if category not in self.categories:
            print("Category does not exist.")
            return

        del self.categories[category]
        print("Category removed.")

    def preset_categories(self):
        try:
            salary_type = input(
                "What is the frequency of your salary? (yearly/monthly/bi-weekly/weekly): "
            ).lower()
            
            if salary_type is "yearly":
                yearly_salary = float(
                    input("Enter your yearly income/salary: ")
                )
                
                self.monthly_salary = yearly_salary / 12
            elif salary_type is "monthly":
                self.monthly_salary = float(
                    input("Enter your monthly income/salary: ")
                )
            elif salary_type is "bi-weekly":
                bi_weekly_salary = float(
                    input("Enter your bi-weekly income/salary: ")
                )  
                self.monthly_salary = bi_weekly_salary * 26 / 12
            elif salary_type is "weekly":
                weekly_salary = float(
                    input("Enter your weekly income/salary: ")
                )
                
                self.monthly_salary = weekly_salary * 52 / 12
            else:
                print("Invalid salary frequency.")
                return
           
        except ValueError:
            print("Salary must be a number.")
            return
        
        if salary_type == "yearly":
            self.yearly_salary = float(input("Enter your yearly income/salary: "))
            self.monthly_salary = self.yearly_salary / 12
            self.bi_weekly_salary = self.yearly_salary / 26
            self.weekly_salary = self.yearly_salary / 52
        elif salary_type == "monthly":
            self.monthly_salary = float(input("Enter your monthly income/salary: "))
            self.yearly_salary = self.monthly_salary * 12
            self.bi_weekly_salary = self.monthly_salary * 12 / 26
            self.weekly_salary = self.monthly_salary * 12 / 52
        elif salary_type == "bi-weekly":
            self.bi_weekly_salary = float(input("Enter your bi-weekly income/salary: "))
            self.monthly_salary = self.bi_weekly_salary * 26 / 12
            self.yearly_salary = self.monthly_salary * 12
            self.weekly_salary = self.bi_weekly_salary / 2
        elif salary_type == "weekly":
            self.weekly_salary = float(input("Enter your weekly income/salary: "))
            self.monthly_salary = self.weekly_salary * 52 / 12
            self.bi_weekly_salary = self.weekly_salary * 2
            self.yearly_salary = self.weekly_salary * 52
        else:
            print("Invalid salary frequency.")
            return

        if self.yearly_salary <= 0:
            print("Yearly salary must be greater than zero.")
            return
        elif self.monthly_salary <= 0:
            print("Monthly salary must be greater than zero.")
            return
        elif self.weekly_salary <= 0:
            print("Weekly salary must be greater than zero.")
            return
        elif self.bi_weekly_salary <= 0:
            print("Bi-weekly salary must be greater than zero.")
            return

        def calculate_salary(salary_type, salary):
            if salary_type == "yearly":
                print(
                    f"Your monthly salary is: ${self.monthly_salary:.2f}\n"
                    f"Your biweekly salary is: ${self.bi_weekly_salary:.2f}\n"
                    f"Your weekly salary is: ${self.weekly_salary:.2f}\n"
                    f"Your yearly salary is: ${self.yearly_salary:.2f}"
                )
                return salary / 12
            elif salary_type == "monthly":
                print(
                    f"Your yearly salary is: ${self.yearly_salary:.2f}\n"
                    f"Your biweekly salary is: ${self.bi_weekly_salary:.2f}\n"
                    f"Your weekly salary is: ${self.weekly_salary:.2f}\n"
                    f"Your monthly salary is: ${self.monthly_salary:.2f}"
                )
                return salary
            elif salary_type == "bi-weekly":
                print(
                    f"Your yearly salary is: ${self.yearly_salary:.2f}\n"
                    f"Your monthly salary is: ${self.monthly_salary:.2f}\n"
                    f"Your weekly salary is: ${self.weekly_salary:.2f}\n"
                    f"Your biweekly salary is: ${self.bi_weekly_salary:.2f}"
                )
                return salary * 26 / 12
            elif salary_type == "weekly":
                print(
                    f"Your yearly salary is: ${self.yearly_salary:.2f}\n"
                    f"Your monthly salary is: ${self.monthly_salary:.2f}\n"
                    f"Your biweekly salary is: ${self.bi_weekly_salary:.2f}\n"
                    f"Your weekly salary is: ${self.weekly_salary:.2f}"
                )
                return salary * 52 / 12
            else:
                raise ValueError("Invalid salary type.")

        self.categories = {
            "Needs": {
                "limit": self.monthly_salary * 0.50,
                "subcategories": {}
            },
            "Wants": {
                "limit": self.monthly_salary * 0.30,
                "subcategories": {}
            },
            "Savings": {
                "limit": self.monthly_salary * 0.20,
                "subcategories": {}
            }
        }

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

        self.categories[category]["limit"] = new_limit
        self.change_count += 1

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

    def save_to_csv(self, filename="budget.csv"):
        try:
            with open(filename, "w", newline="") as file:
                writer = csv.writer(file)

                writer.writerow(
                    [
                        "Category",
                        "Category Limit",
                        "Subcategory",
                        "Subcategory Limit"
                    ]
                )

                for category, info in self.categories.items():
                    subcategories = info["subcategories"]

                    if not subcategories:
                        writer.writerow(
                            [
                                category,
                                info["limit"],
                                "",
                                ""
                            ]
                        )

                    else:
                        for subcategory, sub_limit in subcategories.items():
                            writer.writerow(
                                [
                                    category,
                                    info["limit"],
                                    subcategory,
                                    sub_limit
                                ]
                            )

            print(f"Budget saved to {filename}")

        except Exception as e:
            print(f"Error saving file: {e}")


bank = BankLimit()
bank.menu()
