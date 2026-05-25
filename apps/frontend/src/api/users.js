import { apiClient } from "@/api/client"

export const deleteUserRequest = async (userId) => {
  return apiClient.delete(`/users/${userId}`)
}
