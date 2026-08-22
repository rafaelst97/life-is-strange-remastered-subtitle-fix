local Subtitles = {}

-- Load default Portuguese and fallback English dictionaries
local success_ptb, dict_ptb = pcall(require, "subtitles_PTB")
if success_ptb and dict_ptb then
    Subtitles["PTB"] = dict_ptb
    print("[SubtitleFixMod] Loaded PTB dictionary with " .. tostring(#dict_ptb) .. " entries.")
else
    print("[SubtitleFixMod] Warning: Failed to load subtitles_PTB.lua")
end

local success_int, dict_int = pcall(require, "subtitles_INT")
if success_int and dict_int then
    Subtitles["INT"] = dict_int
end

local active_dict = dict_ptb or dict_int or {}

local function ResolveSubtitle(cue_name)
    if not cue_name then return nil end
    local str_name = tostring(cue_name)
    -- Remove potential whitespace/nulls
    str_name = str_name:gsub("^%s*(.-)%s*$", "%1")
    
    local text = active_dict[str_name]
    if text and text ~= "" then
        return text
    end
    
    if dict_int and dict_int[str_name] then
        return dict_int[str_name]
    end
    
    return nil
end

print("[SubtitleFixMod] SubtitleFixMod initializing...")

-- Hook all possible subtitle functions
local hook_targets = {
    "Function /Script/LiS.LiSGameModeBase:SetSubtitleCue",
    "Function /Script/LiS.WidgetSubtitles:UpdateSubtitlesImplementable",
    "Function /Script/LiS.WidgetSubtitles:UpdateSubtitle",
    "Function /Script/LiS.WidgetSubtitles:UpdateSubtitles",
    "Function /Script/LiS.LiSGameModeBase:UpdateSubtitle",
    "Function /Script/LiS.LiSGameModeBase:UpdateSubtitles",
}

for _, target in ipairs(hook_targets) do
    local ok, err = pcall(function()
        RegisterHook(target, function(self, param1, param2)
            pcall(function()
                -- Check self properties
                local cue = nil
                if self.CurrentSubtitleCue then
                    cue = tostring(self.CurrentSubtitleCue:ToString())
                elseif param1 then
                    cue = tostring(param1:get())
                end
                
                if cue and cue ~= "" and cue ~= "None" then
                    local resolved = ResolveSubtitle(cue)
                    if resolved then
                        if self.CurrentTextSubtitle then
                            self.CurrentTextSubtitle = FText(resolved)
                        end
                        if self.Text then
                            self.Text = FText(resolved)
                        end
                        print("[SubtitleFixMod] Fixed subtitle: " .. cue .. " -> " .. resolved:sub(1, 40) .. "...")
                    end
                end
                
                -- Check if CurrentTextSubtitle contains a raw cue name
                if self.CurrentTextSubtitle then
                    local current_str = tostring(self.CurrentTextSubtitle:ToString())
                    if current_str:sub(1, 4) == "Act_" or current_str:sub(1, 4) == "Cue_" then
                        local resolved = ResolveSubtitle(current_str)
                        if resolved then
                            self.CurrentTextSubtitle = FText(resolved)
                            print("[SubtitleFixMod] Overrode raw key in CurrentTextSubtitle: " .. current_str)
                        end
                    end
                end
            end)
        end)
    end)
    if ok then
        print("[SubtitleFixMod] Hook registered for: " .. target)
    else
        print("[SubtitleFixMod] Could not hook: " .. target .. " (reason: " .. tostring(err) .. ")")
    end
end

-- Also register a global Pre/Post hook on ProcessEvent or general UObject lifecycle if needed
print("[SubtitleFixMod] SubtitleFixMod active and ready!")
