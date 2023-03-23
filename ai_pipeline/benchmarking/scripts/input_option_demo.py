options = ['ei-sample', 'ei-infer', 'NO']

print('Please select an option:')
for i, option in enumerate(options):
    print(f'{i + 1}: {option}')

selected_option = None
while selected_option is None:
    try:
        choice = int(input('Enter the number of your choice: '))
        if choice < 1 or choice > len(options):
            raise ValueError
        selected_option = options[choice - 1]
    except ValueError:
        print('Invalid choice. Please enter a number between 1 and', len(options))

print(f'You selected: {selected_option}')