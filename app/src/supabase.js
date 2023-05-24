import { createClient } from '@supabase/supabase-js'

const DB = createClient("https://tecskhekxfsziaiqpuxj.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRlY3NraGVreGZzemlhaXFwdXhqIiwicm9sZSI6ImFub24iLCJpYXQiOjE2ODQ2NzA1MjEsImV4cCI6MjAwMDI0NjUyMX0.qIZePGL2cSyY4akQgo_hm3Zemnn0YUwxaSaZqF_crUk")

export async function getRandom() {
    const result = await DB.from('en_simple').select('answer').limit(1)
    return result.data.map(x => x.answer)
}

export async function getRegex(regex) {
    const result = await DB.from('en_simple').select('answer').match({question: regex})
    return result.data.map(x => x.answer)
}

export async function getRegexWithAlphabit(regex, alphabit) {
    const result = await DB.from('en_simple').select('answer').where(`is_bitwise_or_all_ones('${alphabit.to01()}':bit(26), alphabit)`).match({question: regex})
    return result.data.map(x => x.answer)
}