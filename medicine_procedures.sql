-- PostgreSQL Stored Procedures for Medicine Model
-- Generated based on MedicineModel from app/medicine/models.py

-- ========================================
-- MEDICINE MODEL PROCEDURES
-- ========================================

-- CreateMedicine procedure
CREATE OR REPLACE FUNCTION CreateMedicine(
    p_created_at TIMESTAMP,
    p_updated_at TIMESTAMP,
    p_name VARCHAR(63),
    p_description VARCHAR(511),
    p_intake_type VARCHAR(31),
    p_dose NUMERIC,
    p_measurement VARCHAR(31)
) RETURNS TABLE(
    id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name VARCHAR(63),
    description VARCHAR(511),
    intake_type VARCHAR(31),
    dose NUMERIC,
    measurement VARCHAR(31)
) AS $$
BEGIN
    INSERT INTO medicines (created_at, updated_at, name, description, intake_type, dose, measurement)
    VALUES (p_created_at, p_updated_at, p_name, p_description, p_intake_type, p_dose, p_measurement)
    RETURNING * INTO id, created_at, updated_at, name, description, intake_type, dose, measurement;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- UpdateMedicine procedure
CREATE OR REPLACE FUNCTION UpdateMedicine(
    p_id INTEGER,
    p_created_at TIMESTAMP DEFAULT NULL,
    p_updated_at TIMESTAMP DEFAULT NULL,
    p_name VARCHAR(63) DEFAULT NULL,
    p_description VARCHAR(511) DEFAULT NULL,
    p_intake_type VARCHAR(31) DEFAULT NULL,
    p_dose NUMERIC DEFAULT NULL,
    p_measurement VARCHAR(31) DEFAULT NULL
) RETURNS TABLE(
    id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name VARCHAR(63),
    description VARCHAR(511),
    intake_type VARCHAR(31),
    dose NUMERIC,
    measurement VARCHAR(31)
) AS $$
BEGIN
    UPDATE medicines 
    SET 
        created_at = COALESCE(p_created_at, created_at),
        updated_at = COALESCE(p_updated_at, updated_at),
        name = COALESCE(p_name, name),
        description = COALESCE(p_description, description),
        intake_type = COALESCE(p_intake_type, intake_type),
        dose = COALESCE(p_dose, dose),
        measurement = COALESCE(p_measurement, measurement)
    WHERE id = p_id
    RETURNING * INTO id, created_at, updated_at, name, description, intake_type, dose, measurement;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Medicine not found with id: %', p_id;
    END IF;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- FindMedicine procedure
CREATE OR REPLACE FUNCTION FindMedicine(
    p_order_by_column VARCHAR(50) DEFAULT 'id',
    p_order_by_direction VARCHAR(4) DEFAULT 'ASC',
    p_last_id INTEGER DEFAULT NULL,
    p_last_value ANYELEMENT DEFAULT NULL,
    p_limit INTEGER DEFAULT 50
) RETURNS TABLE(
    id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name VARCHAR(63),
    description VARCHAR(511),
    intake_type VARCHAR(31),
    dose NUMERIC,
    measurement VARCHAR(31)
) AS $$
DECLARE
    query_text TEXT;
    where_clause TEXT := '';
BEGIN
    query_text := 'SELECT * FROM medicines';
    
    -- Handle cursor-based pagination with last attribute
    IF p_last_id IS NOT NULL THEN
        IF p_order_by_direction = 'ASC' THEN
            IF p_order_by_column != 'id' AND p_last_value IS NOT NULL THEN
                where_clause := ' WHERE (' || p_order_by_column || ' > ' || quote_literal(p_last_value) || 
                               ' OR (' || p_order_by_column || ' = ' || quote_literal(p_last_value) || 
                               ' AND id > ' || p_last_id || '))';
            ELSE
                where_clause := ' WHERE id > ' || p_last_id;
            END IF;
        ELSE
            IF p_order_by_column != 'id' AND p_last_value IS NOT NULL THEN
                where_clause := ' WHERE (' || p_order_by_column || ' < ' || quote_literal(p_last_value) || 
                               ' OR (' || p_order_by_column || ' = ' || quote_literal(p_last_value) || 
                               ' AND id < ' || p_last_id || '))';
            ELSE
                where_clause := ' WHERE id < ' || p_last_id;
            END IF;
        END IF;
    END IF;
    
    query_text := query_text || where_clause;
    
    -- Add ordering
    query_text := query_text || ' ORDER BY ' || p_order_by_column || ' ' || p_order_by_direction;
    
    -- Add secondary ordering by id if not already ordering by id
    IF p_order_by_column != 'id' THEN
        query_text := query_text || ', id ' || p_order_by_direction;
    END IF;
    
    -- Add pagination
    query_text := query_text || ' LIMIT ' || p_limit;
    
    RETURN QUERY EXECUTE query_text;
END;
$$ LANGUAGE plpgsql;

-- FindOneMedicine procedure
CREATE OR REPLACE FUNCTION FindOneMedicine(p_id INTEGER)
RETURNS TABLE(
    id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name VARCHAR(63),
    description VARCHAR(511),
    intake_type VARCHAR(31),
    dose NUMERIC,
    measurement VARCHAR(31)
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM medicines WHERE id = p_id;
END;
$$ LANGUAGE plpgsql;

-- DeleteMedicine procedure
CREATE OR REPLACE FUNCTION DeleteMedicine(p_id INTEGER)
RETURNS TABLE(
    id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name VARCHAR(63),
    description VARCHAR(511),
    intake_type VARCHAR(31),
    dose NUMERIC,
    measurement VARCHAR(31)
) AS $$
DECLARE
    deleted_record RECORD;
BEGIN
    DELETE FROM medicines 
    WHERE id = p_id
    RETURNING * INTO deleted_record;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Medicine not found with id: %', p_id;
    END IF;
    
    RETURN QUERY SELECT * FROM deleted_record;
END;
$$ LANGUAGE plpgsql;

-- UpsertMedicine procedure
CREATE OR REPLACE FUNCTION UpsertMedicine(
    p_id INTEGER DEFAULT NULL,
    p_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    p_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    p_name VARCHAR(63) DEFAULT NULL,
    p_description VARCHAR(511) DEFAULT NULL,
    p_intake_type VARCHAR(31) DEFAULT NULL,
    p_dose NUMERIC DEFAULT NULL,
    p_measurement VARCHAR(31) DEFAULT NULL
) RETURNS TABLE(
    id INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    name VARCHAR(63),
    description VARCHAR(511),
    intake_type VARCHAR(31),
    dose NUMERIC,
    measurement VARCHAR(31)
) AS $$
BEGIN
    IF p_id IS NULL THEN
        -- Insert new record
        INSERT INTO medicines (created_at, updated_at, name, description, intake_type, dose, measurement)
        VALUES (p_created_at, p_updated_at, p_name, p_description, p_intake_type, p_dose, p_measurement)
        RETURNING * INTO id, created_at, updated_at, name, description, intake_type, dose, measurement;
    ELSE
        -- Update existing record
        UPDATE medicines 
        SET 
            created_at = COALESCE(p_created_at, created_at),
            updated_at = COALESCE(p_updated_at, updated_at),
            name = COALESCE(p_name, name),
            description = COALESCE(p_description, description),
            intake_type = COALESCE(p_intake_type, intake_type),
            dose = COALESCE(p_dose, dose),
            measurement = COALESCE(p_measurement, measurement)
        WHERE id = p_id
        RETURNING * INTO id, created_at, updated_at, name, description, intake_type, dose, measurement;
        
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Medicine not found with id: %', p_id;
        END IF;
    END IF;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- TABLE CREATION
-- ========================================

-- Medicines table
CREATE TABLE IF NOT EXISTS medicines (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(63) NOT NULL,
    description VARCHAR(511) NOT NULL,
    intake_type VARCHAR(31) NOT NULL,
    dose NUMERIC NOT NULL CHECK (dose > 0),
    measurement VARCHAR(31) NOT NULL
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_medicines_name ON medicines(name);
CREATE INDEX IF NOT EXISTS idx_medicines_intake_type ON medicines(intake_type);
CREATE INDEX IF NOT EXISTS idx_medicines_created_at ON medicines(created_at); 