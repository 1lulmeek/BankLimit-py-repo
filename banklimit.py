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
            print("7. Exit")

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
                print("Exiting the program. Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def add_category(self):
        category = input("Enter the category: ").title()
        try:
            limit = float(input("Enter the limit: "))
        except ValueError:
            print("The limit must be a number.")
            return
        except EOFError:
            print("Input error. Please try again.")
            return
        if limit < 0:
            print("Limit cannot be negative.")
            return
        else:
            print(f"Category '{category}' added with limit ${limit:.2f}.")

        subcategory = input(
            "Would you like to add a subcategory? (yes/no): "
        ).lower()
        if subcategory == "yes":
            subcategory = input("Enter the subcategory: ").title()
            try:
                limit = float(input("Enter the limit for the subcategory: "))
            except ValueError:
                print("The limit must be a number.")
                return
            except EOFError:
                print("Input error. Please try again.")
                return
            if limit < 0:
                print("Limit cannot be negative.")
                return

            if isinstance(self.categories[category], dict):
                self.categories[category][subcategory] = limit
            else:
                self.categories[category] = {subcategory: limit}

            print(f"Subcategory '{subcategory}' added under '{category}'.")
        else:
            self.categories[category] = limit
        print("Category added.")

    def show_categories(self):
        if not self.categories:
            print("No categories have been added.")
            return

        for category, limit in self.categories.items():
            print(f"{category}: ${limit:.2f}")

    def view_total_budget(self):
        total = self.monthly_salary
        print(f"Total Budget: ${total:.2f}")
        allocated = sum(self.categories.values())
        print(f"Allocated Budget: ${allocated:.2f}")
        remaining = total - allocated
        print(f"Remaining Budget: ${remaining:.2f}")

    def remove_category(self):
        print("Current Categories:")
        for category, limit in self.categories.items():
            print(f"{category}: ${limit:.2f}")

        category = input("Enter the category to remove: ").title()

        if category not in self.categories:
            print("Category does not exist.")
            return

        del self.categories[category]
        print("Category removed.")

    def preset_categories(self):
        try:
            yearly_salary = float(input("Enter your yearly income/salary: "))
        except ValueError:
            print("Salary must be a number.")
            return
        except EOFError:
            print("Input error. Please try again.")
            return

        if yearly_salary < 0:
            print("Yearly salary cannot be negative.")
            return

        self.yearly_salary = yearly_salary
        self.monthly_salary = yearly_salary / 12
        print(f"Your monthly salary is: ${self.monthly_salary:.2f}")

        self.categories = {
            "Needs": self.monthly_salary * 0.50,
            "Wants": self.monthly_salary * 0.30,
            "Savings": self.monthly_salary * 0.20,
        }

        choose_subcategory = input(
            "Would you like to add subcategories to the preset "
            "categories? (yes/no): "
        ).lower()

        if choose_subcategory == "yes":
            for category in ["Needs", "Wants", "Savings"]:
                add_sub = input(
                    "Would you like to add subcategories to "
                    f"{category}? (yes/no): "
                ).lower()
                if add_sub == "yes":
                    while True:
                        subcategory = input(
                            "Enter a subcategory for "
                            f"{category} (or type 'done' to finish): "
                        ).title()
                        if subcategory.lower() == "done":
                            break
                        try:
                            limit = float(
                                input(f"Enter the limit for {subcategory}: ")
                            )
                        except ValueError:
                            print("The limit must be a number.")
                            continue
                        except EOFError:
                            print("Input error. Please try again.")
                            continue
                        if limit < 0:
                            print("Limit cannot be negative.")
                            continue

                        if isinstance(self.categories[category], dict):
                            self.categories[category][subcategory] = limit
                        else:
                            self.categories[category] = {subcategory: limit}

                        print(
                            f"Subcategory '{subcategory}' added under "
                            f"'{category}'."
                        )

        print("50/30/20 preset added.")

        def category_total(value):
            if isinstance(value, dict):
                return sum(value.values())
            return value

        preset_total = sum(
            category_total(value)
            for value in self.categories.values()
        )

        for category, value in self.categories.items():
            if isinstance(value, dict):
                print(
                    f"{category}: ${sum(value.values()):.2f} "
                    "(subtotal from subcategories)"
                )
            else:
                print(f"{category}: ${value:.2f}")
        print(f"Total: ${preset_total:.2f}")

        if preset_total > self.monthly_salary:
            print(
                "Warning: The total of preset categories exceeds "
                "your monthly salary."
            )

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

        except EOFError:
            print("Input error. Please try again.")
            return

        if new_limit < 0:
            print("Limit cannot be negative.")
            return

        old_limit = self.categories[category]
        self.categories[category] = new_limit
        self.change_count += 1

        changes_left = self.max_changes - self.change_count

        msg1 = (
            f"{category} changed from ${old_limit:.2f} to "
            f"${new_limit:.2f}."
        )
        msg2 = f"Changes used: {self.change_count}/{self.max_changes}."
        msg3 = f"Changes remaining: {changes_left}."
        print(msg1)
        print(msg2)
        print(msg3)

        if self.change_count >= self.max_changes:
            self.locked = True
            print("Your budget is now locked for this month.")

    def save_to_csv(self, filename="budget.csv"):
        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Category", "Limit"])
                for category, limit in self.categories.items():
                    writer.writerow([category, limit])
            print(f"Budget saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {e}")
        except Exception as e:
            print(f"Error saving file: {e}")


bank = BankLimit()
bank.menu()
