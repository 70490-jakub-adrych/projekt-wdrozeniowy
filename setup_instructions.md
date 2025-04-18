# System Setup Instructions

## Setting Up Demo Data

To quickly set up the system with demo data including organizations, users, and tickets, run the following command:

```bash
python manage.py setup_demo_data
```

This will:

1. Create user groups with appropriate permissions
2. Create sample organizations
3. Create admin, agent, and client user accounts
4. Create sample tickets with various statuses
5. Output login credentials for the created accounts

## Demo User Accounts

After running the command, you can log in with these credentials:

- Admin: username=admin, password=admin123
- Agent 1: username=agent1, password=agent123
- Agent 2: username=agent2, password=agent123
- Client 1: username=client1, password=client123
- Client 2: username=client2, password=client123
- and so on...

## Production Setup

For production environments, you should:

1. Run the command to set up groups and permissions:
   ```bash
   python manage.py setup_demo_data
   ```

2. Create a real admin account:
   ```bash
   python manage.py createsuperuser
   ```

3. Don't use the demo accounts in production.
