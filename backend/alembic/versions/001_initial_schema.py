"""Initial schema creation

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('idx_user_username', 'users', ['username'])
    op.create_index('idx_user_email', 'users', ['email'])

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token'),
    )
    op.create_index('idx_session_user_id', 'sessions', ['user_id'])
    op.create_index('idx_session_token', 'sessions', ['token'])
    op.create_index('idx_session_expires_at', 'sessions', ['expires_at'])

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('target_url', sa.String(2000), nullable=False),
        sa.Column('fetcher_type', sa.Enum('http', 'dynamic', 'stealthy', name='fetchertype'), nullable=False),
        sa.Column('selector', sa.String(1000), nullable=False),
        sa.Column('selector_type', sa.Enum('css', 'xpath', name='selectortype'), nullable=False),
        sa.Column('timeout', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.Enum('draft', 'running', 'paused', 'completed', 'failed', 'stopped', name='taskstatus'), nullable=False, server_default='draft'),
        sa.Column('use_proxy_rotation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('solve_cloudflare', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('custom_headers', sa.JSON(), nullable=True),
        sa.Column('cookies', sa.JSON(), nullable=True),
        sa.Column('wait_time', sa.Integer(), nullable=True),
        sa.Column('viewport_width', sa.Integer(), nullable=True),
        sa.Column('viewport_height', sa.Integer(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('total_runs', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('success_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_task_user_id', 'tasks', ['user_id'])
    op.create_index('idx_task_status', 'tasks', ['status'])
    op.create_index('idx_task_created_at', 'tasks', ['created_at'])
    op.create_index('idx_task_user_status', 'tasks', ['user_id', 'status'])

    # Create results table
    op.create_table(
        'results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('source_url', sa.String(2000), nullable=False),
        sa.Column('extracted_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_result_task_id', 'results', ['task_id'])
    op.create_index('idx_result_extracted_at', 'results', ['extracted_at'])

    # Create task_logs table
    op.create_table(
        'task_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('level', sa.Enum('DEBUG', 'INFO', 'WARNING', 'ERROR', name='loglevel'), nullable=False),
        sa.Column('message', sa.String(2000), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_tasklog_task_id', 'task_logs', ['task_id'])
    op.create_index('idx_tasklog_timestamp', 'task_logs', ['timestamp'])
    op.create_index('idx_tasklog_level', 'task_logs', ['level'])

    # Create proxies table
    op.create_table(
        'proxies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('protocol', sa.Enum('http', 'https', 'socks5', name='proxyprotocol'), nullable=False),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('port', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('password', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_proxy_user_id', 'proxies', ['user_id'])
    op.create_index('idx_proxy_is_active', 'proxies', ['is_active'])

    # Create headers table
    op.create_table(
        'headers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(255), nullable=False),
        sa.Column('value', sa.String(1000), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_header_user_id', 'headers', ['user_id'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_index('idx_header_user_id', table_name='headers')
    op.drop_table('headers')
    
    op.drop_index('idx_proxy_is_active', table_name='proxies')
    op.drop_index('idx_proxy_user_id', table_name='proxies')
    op.drop_table('proxies')
    
    op.drop_index('idx_tasklog_level', table_name='task_logs')
    op.drop_index('idx_tasklog_timestamp', table_name='task_logs')
    op.drop_index('idx_tasklog_task_id', table_name='task_logs')
    op.drop_table('task_logs')
    
    op.drop_index('idx_result_extracted_at', table_name='results')
    op.drop_index('idx_result_task_id', table_name='results')
    op.drop_table('results')
    
    op.drop_index('idx_task_user_status', table_name='tasks')
    op.drop_index('idx_task_created_at', table_name='tasks')
    op.drop_index('idx_task_status', table_name='tasks')
    op.drop_index('idx_task_user_id', table_name='tasks')
    op.drop_table('tasks')
    
    op.drop_index('idx_session_expires_at', table_name='sessions')
    op.drop_index('idx_session_token', table_name='sessions')
    op.drop_index('idx_session_user_id', table_name='sessions')
    op.drop_table('sessions')
    
    op.drop_index('idx_user_email', table_name='users')
    op.drop_index('idx_user_username', table_name='users')
    op.drop_table('users')
