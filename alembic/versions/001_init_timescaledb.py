"""Initialize TimescaleDB and create hypertables

Revision ID: 001_init_timescaledb
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_init_timescaledb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable TimescaleDB extension
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE")

    # Create signals hypertable for time-series event data
    op.create_table(
        'signals',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_id', sa.String(36), nullable=False),
        sa.Column('correlation_id', sa.String(36), nullable=True),
        sa.Column('source_system', sa.String(50), nullable=False),
        sa.Column('source_component', sa.String(100), nullable=False),
        sa.Column('node_ref', sa.String(200), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('payload', sa.JSON, nullable=True),
        sa.PrimaryKeyConstraint('time', 'event_id')
    )

    # Convert to hypertable (time-series optimized)
    op.execute(
        "SELECT create_hypertable('signals', 'time', "
        "chunk_time_interval => INTERVAL '1 day')"
    )

    # Create indexes for common queries
    op.create_index(
        'idx_signals_node_ref',
        'signals',
        ['node_ref', 'time']
    )
    op.create_index(
        'idx_signals_event_type',
        'signals',
        ['event_type', 'time']
    )
    op.create_index(
        'idx_signals_correlation',
        'signals',
        ['correlation_id']
    )

    # Create metrics hypertable for time-series metrics
    op.create_table(
        'metrics',
        sa.Column('time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('value', sa.Float, nullable=False),
        sa.Column('tags', sa.JSON, nullable=True),
        sa.PrimaryKeyConstraint('time', 'name')
    )

    # Convert to hypertable
    op.execute(
        "SELECT create_hypertable('metrics', 'time', "
        "chunk_time_interval => INTERVAL '1 hour')"
    )

    # Create index for metric queries
    op.create_index(
        'idx_metrics_name',
        'metrics',
        ['name', 'time']
    )

    # Enable compression on signals (after 7 days)
    op.execute(
        "ALTER TABLE signals SET ("
        "timescaledb.compress, "
        "timescaledb.compress_segmentby = 'node_ref'"
        ")"
    )
    op.execute(
        "SELECT add_compression_policy('signals', INTERVAL '7 days')"
    )

    # Enable compression on metrics (after 1 day)
    op.execute(
        "ALTER TABLE metrics SET ("
        "timescaledb.compress, "
        "timescaledb.compress_segmentby = 'name'"
        ")"
    )
    op.execute(
        "SELECT add_compression_policy('metrics', INTERVAL '1 day')"
    )

    # Create continuous aggregate for hourly signal counts
    op.execute("""
        CREATE MATERIALIZED VIEW signal_counts_hourly
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 hour', time) AS bucket,
            node_ref,
            event_type,
            COUNT(*) as count
        FROM signals
        GROUP BY bucket, node_ref, event_type
        WITH NO DATA
    """)

    # Add refresh policy for continuous aggregate
    op.execute(
        "SELECT add_continuous_aggregate_policy('signal_counts_hourly', "
        "start_offset => INTERVAL '3 hours', "
        "end_offset => INTERVAL '1 hour', "
        "schedule_interval => INTERVAL '1 hour')"
    )

    # Create continuous aggregate for metric averages
    op.execute("""
        CREATE MATERIALIZED VIEW metric_averages_hourly
        WITH (timescaledb.continuous) AS
        SELECT
            time_bucket('1 hour', time) AS bucket,
            name,
            AVG(value) as avg_value,
            MIN(value) as min_value,
            MAX(value) as max_value,
            COUNT(*) as sample_count
        FROM metrics
        GROUP BY bucket, name
        WITH NO DATA
    """)

    op.execute(
        "SELECT add_continuous_aggregate_policy('metric_averages_hourly', "
        "start_offset => INTERVAL '3 hours', "
        "end_offset => INTERVAL '1 hour', "
        "schedule_interval => INTERVAL '1 hour')"
    )


def downgrade() -> None:
    # Drop continuous aggregates
    op.execute("DROP MATERIALIZED VIEW IF EXISTS metric_averages_hourly CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS signal_counts_hourly CASCADE")

    # Drop tables (this also removes hypertable metadata)
    op.drop_table('metrics')
    op.drop_table('signals')

    # Note: We don't drop the timescaledb extension as other tables may use it
