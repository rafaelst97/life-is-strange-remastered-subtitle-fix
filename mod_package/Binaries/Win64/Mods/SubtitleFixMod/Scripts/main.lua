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
    str_name = str_name:gsub("^%s*(.-)%s*$", "%1")
    
    local text = active_dict[str_name]
    if text and text ~= "" then
        return text
    end
    
    -- Also try looking for partial key or stripped prefix
    if str_name:sub(1, 4) == "Cue_" then
        local sub_key = str_name:sub(5)
        if active_dict[sub_key] then return active_dict[sub_key] end
    end
    
    -- Try searching key that ends with the action/cue
    for k, v in pairs(active_dict) do
        if k == str_name or k:find(str_name, 1, true) then
            return v
        end
    end
    
    return nil
end

local function AutoApplyLanguageFix()
    pcall(function()
        local alt_data_list = FindAllOf("DNEAltData") or {}
        for _, alt in ipairs(alt_data_list) do
            if alt and alt:IsValid() and alt.SetSubtitleLanguage then
                alt:SetSubtitleLanguage("pt-BR")
                print("[SubtitleFixMod] Called SetSubtitleLanguage('pt-BR') on DNEAltData instance.")
            end
        end
    end)
    
    pcall(function()
        local gi_list = FindAllOf("LiSGameInstance") or {}
        for _, gi in ipairs(gi_list) do
            if gi and gi:IsValid() and gi.BP_ChangeLanguage then
                gi:BP_ChangeLanguage("pt-BR")
                print("[SubtitleFixMod] Called BP_ChangeLanguage('pt-BR') on LiSGameInstance.")
            end
        end
    end)
end

print("[SubtitleFixMod] SubtitleFixMod initializing hooks...")

-- 1. Auto-trigger on Level / Controller start
local level_hooks = {
    "Function /Script/Engine.PlayerController:ClientRestart",
    "Function /Script/Engine.GameModeBase:StartPlay",
    "Function /Script/Engine.Actor:ReceiveBeginPlay",
}

for _, target in ipairs(level_hooks) do
    pcall(function()
        RegisterHook(target, function(self)
            AutoApplyLanguageFix()
        end)
    end)
end

-- 2. Hook Subtitle Widgets and GameMode
local hook_targets = {
    "Function /Script/LiS.LiSGameModeBase:SetSubtitleCue",
    "Function /Script/LiS.WidgetSubtitles:UpdateSubtitlesImplementable",
    "Function /Script/LiS.WidgetSubtitles:UpdateSubtitle",
    "Function /Script/LiS.WidgetSubtitles:UpdateSubtitles",
    "Function /Script/LiS.LiSGameModeBase:UpdateSubtitle",
    "Function /Script/LiS.LiSGameModeBase:UpdateSubtitles",
    "Function /Script/UMG.TextBlock:SetText",
}

for _, target in ipairs(hook_targets) do
    pcall(function()
        RegisterHook(target, function(self, param1, param2)
            pcall(function()
                -- Check self properties
                local cue = nil
                if self.CurrentSubtitleCue then
                    cue = tostring(self.CurrentSubtitleCue:ToString())
                elseif param1 and type(param1) == "userdata" and param1.ToString then
                    cue = tostring(param1:ToString())
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
                    end
                end
                
                -- Check if CurrentTextSubtitle contains a raw cue name or action token
                if self.CurrentTextSubtitle then
                    local current_str = tostring(self.CurrentTextSubtitle:ToString())
                    if current_str:sub(1, 4) == "Act_" or current_str:sub(1, 4) == "Cue_" or current_str:find("PhotoLook") then
                        local resolved = ResolveSubtitle(current_str)
                        if resolved then
                            self.CurrentTextSubtitle = FText(resolved)
                        end
                    end
                end
            end)
        end)
    end)
end

-- Initial trigger on script boot
AutoApplyLanguageFix()
print("[SubtitleFixMod] SubtitleFixMod active with auto-trigger & UTextBlock resolvers!")
