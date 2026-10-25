class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
        index=True
    )

    source_type = Column(
        String(100),
        nullable=False
    )

    source_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    relationship_type = Column(
        String(100),
        nullable=False,
        index=True
    )

    target_type = Column(
        String(100),
        nullable=False
    )

    target_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )