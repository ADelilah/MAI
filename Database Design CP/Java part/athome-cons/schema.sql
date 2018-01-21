CREATE OR REPLACE FUNCTION Moderation(who INTEGER, activity INTEGER, comm INTEGER)
  RETURNS TEXT AS $$
DECLARE
  warn BOOLEAN := FALSE;
  warned BOOLEAN := FALSE;
  finalcase TEXT := 'moderation failed';
BEGIN

  -- activity deletion case
  IF comm = 0 THEN
    IF NOT EXISTS(SELECT * FROM activities
    WHERE act_id=activity AND citizen_id=who)
    THEN finalcase:= 'User already deleted the activity';
    ELSE DELETE FROM activities WHERE act_id=activity;
      warn := TRUE;
    END IF;
  END IF;

  -- comment burning case
  IF comm != 0
  THEN
    IF NOT EXISTS(SELECT * FROM activities_comments WHERE act_comment_id = comm
                                                          AND act_id=activity
                                                          AND citizen_id=who)
    THEN finalcase:= 'This comment does not exist'; -- +
    ELSE UPDATE activities_comments
    SET act_comment_text = 'This comment was removed by moderator because it violates the Terms of Service'
    WHERE act_comment_id = comm AND act_id=activity AND citizen_id=who;
      warn := TRUE;
    END IF;
  END IF;



  -- if warning needed
  IF warn IS TRUE
  THEN
    -- 1st warning
    IF NOT EXISTS(SELECT * FROM bad WHERE citizen_id = who)
    THEN INSERT INTO bad VALUES (citizen_id = who, two_warn=FALSE);
      finalcase:= 'First warning added';
      -- 2d warning
    ELSEIF NOT (SELECT two_warn FROM bad WHERE citizen_id=who)
      THEN UPDATE bad SET two_warn = TRUE WHERE citizen_id=who;
        finalcase:= 'Second warning added';
        -- Ban
    ELSE UPDATE bad b SET b.ban_date = current_timestamp;
      finalcase:= 'User banned';
    END IF;
  END IF;

  RETURN finalcase;

END;
$$ LANGUAGE plpgsql;

---------------------------------------------------------------------------------
---------------------------------------------------------------------------------

CREATE FUNCTION Timeline() RETURNS trigger AS $timeline$
-- Trigger checks that: now < start time < end time < now + 6 month
DECLARE
  error_message TEXT;
BEGIN
  -- start < end
  IF activities.act_start_time > activities.act_end_time
    THEN
      error_message := 'End time should be later than start time';
      RAISE EXCEPTION 'End time should be later than start time';
  END IF;

  -- now < start
  IF current_timestamp > activities.act_start_time OR activities.act_end_time > (current_timestamp + '6 month'::interval)
    THEN
      error_message := 'Activity should start and end within next two months';
      RAISE EXCEPTION 'Activity should start and end within next two months';
  END IF;

  RETURN error_message;
END;
$timeline$ LANGUAGE plpgsql;

CREATE TRIGGER Timeline BEFORE INSERT OR UPDATE ON activities
FOR EACH ROW EXECUTE PROCEDURE Timeline();

---------------------------------------------------------------------------------
---------------------------------------------------------------------------------

CREATE FUNCTION Timeline_join() RETURNS trigger AS $timelinej$
-- Trigger doesn't allow to join / leave a past activity
DECLARE
  error_message TEXT;
BEGIN
  -- start < end
  IF (SELECT a.act_end_time FROM activities a
      WHERE activities_participants.act_id = a.act_id) > current_timestamp
  THEN
    error_message := 'You are trying to change the past, man';
    RAISE EXCEPTION 'Cannot join/leave activity because it has over';
  END IF;

  RETURN error_message;
END;
$timelinej$ LANGUAGE plpgsql;

CREATE TRIGGER Timeline_join BEFORE INSERT OR UPDATE ON activities_participants
FOR EACH ROW EXECUTE PROCEDURE Timeline_join();